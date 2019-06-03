import abc
import copy
import logging
import multiprocessing

import pm4py.objects.log.util.log as log_util
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.algo.discovery.est_miner.utils.place_fitness \
import PlaceFitnessEvaluator, PlaceFitness
from pm4py.algo.discovery.est_miner.utils.activity_order \
import ActivityOrder, max_element, min_element
from pm4py.algo.discovery.est_miner.utils import est_utils

class SearchStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(
        self,
        log,
        tau,
        pre_pruning_strategy,
        in_order,
        out_order,
        activities,
        start_activity,
        end_activity,
        logger=None,
        stat_logger=None
    ):
        """
        Strategy how to search through the candidate space,
        when to cut off search and where to start and finish.
        """
        pass

class TreeDfsStrategy(SearchStrategy):
    class RootExtractor:

        @classmethod
        def get_roots(cls, activities, start_activity, end_activity, pre_pruning_strategy):
            roots = set()
            for a1 in activities:
                for a2 in activities:
                    p = Place(a1, a2, 1, 1)
                    if not pre_pruning_strategy.execute(p, start_activity, end_activity):
                        roots.add(p)
            return roots
    
    def __init__(self, restricted_edge_type):
        assert(restricted_edge_type == 'red' or restricted_edge_type == 'blue')
        self._restricted_edge_type = restricted_edge_type
    
    def execute(self, log, tau, pre_pruning_strategy, in_order, out_order, activities, start_activity, end_activity, logger=None, stat_logger=None):
        if (logger is not None):
            logger.info('Starting Search')
        roots = self.RootExtractor.get_roots(activities, start_activity, end_activity, pre_pruning_strategy)
        return self.traverse_roots(
            roots,
            log,
            tau,
            in_order,
            out_order,
            pre_pruning_strategy,
            activities,
            start_activity,
            end_activity,
            logger=logger,
            stat_logger=stat_logger
        )

    def traverse_roots(
        self,
        roots,
        log,
        tau,
        in_order,
        out_order,
        pre_pruning_strategy,
        activities,
        start_activity,
        end_activity,
        logger=None,
        stat_logger=None
    ):
        fitting_places = list()
        args = list()
        for root in roots:
            #fitting_places.extend(self._traverse_place(log, tau, root, in_order, out_order, pre_pruning_strategy, activities, start_activity, end_activity, logger=logger, stat_logger=stat_logger))
            args.append( (log, tau, root, in_order, out_order, pre_pruning_strategy, activities, start_activity, end_activity) )
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            fitting_places = pool.starmap(self._traverse_place, args)
        
        flat_result = [p for fitting in fitting_places for p in fitting]
        return flat_result
        #return fitting_places
    
    def _traverse_place(
        self,
        log,
        tau,
        place,
        in_order,
        out_order,
        pre_pruning_strategy,
        activities,
        start_activity,
        end_activity,
        logger=None,
        stat_logger=None
    ):
        if logger is not None:
            logger.info('Checking node ' + place.name)
        
        if pre_pruning_strategy.execute(place, start_activity, end_activity):
            if logger is not None:
                logger.info('    Pre-pruning the node.')
            return list()
        
        fitting_places = list()
        place_fitness_states = PlaceFitnessEvaluator.evaluate_place_fitness(
            log, 
            place, 
            tau
        )

        child_places = list()
        if PlaceFitness.FITTING in place_fitness_states:
            if logger is not None:
                logger.info('    Place is fitting.')
            fitting_places.append(place)
        
        if (
            PlaceFitness.OVERFED not in place_fitness_states 
            or (self._restricted_edge_type == 'red' 
            and self._cant_prune_red_subtrees(place, out_order, activities))
        ): # nodes attached by red edge
            child_places.extend(self._get_red_child_places(place, in_order, activities))
        elif stat_logger is not None:
            stat_logger.pruned_red_subtree(place)
        if (
            PlaceFitness.UNDERFED not in place_fitness_states
            or (self._restricted_edge_type == 'blue'
            and self._cant_prune_blue_subtrees(place, in_order, activities))
        ): # nodes attached by blue edge
            child_places.extend(self._get_blue_child_places(place, out_order, activities))
        elif stat_logger is not None:
            stat_logger.pruned_blue_subtree(place)
        
        if logger is not None:
            if PlaceFitness.OVERFED in place_fitness_states:
                logger.info('    Place is overfed.')
            if PlaceFitness.UNDERFED in place_fitness_states:
                logger.info('    Place is underfed.')
            logger.info('    ' + str(len(child_places)) + ' child places.')
            for p in child_places:
                logger.info('    Child Place: ' + p.name)

        for p in child_places:
            fitting_places.extend(self._traverse_place(
                log,
                tau,
                p,
                in_order,
                out_order,
                pre_pruning_strategy,
                activities,
                start_activity,
                end_activity,
                logger=logger,
                stat_logger=stat_logger
            ))
        return fitting_places
    
    def _cant_prune_red_subtrees(self, place, out_order, activities):
        max_output_activity = max_element(activities, place.output_trans, out_order)
        return len(out_order.is_larger_relations[max_output_activity]) > 0
    
    def _cant_prune_blue_subtrees(self, place, in_order, activities):
        max_input_activity = max_element(place.input_trans, in_order, activities)
        return len(in_order.is_larger_relations[max_input_activity]) > 0
    
    def _get_red_child_places(self, place, in_order, activities):
        if (self._restricted_edge_type == 'red'):
            if (place.num_output_trans > 1):
                return list()
        
        child_places = list()
        max_input_activity = max_element(activities, place.input_trans, in_order)
        higher_ordered_activities = in_order.is_larger_relations[max_input_activity]
        for a in higher_ordered_activities:
            new_input_trans = copy.copy(place.input_trans)
            new_input_trans = new_input_trans | a
            num_input_trans = copy.copy(place.num_input_trans) + 1
            child_places.append(Place(new_input_trans, copy.copy(place.output_trans), num_input_trans, copy.copy(place.num_output_trans)))
        return child_places
    
    def _get_blue_child_places(self, place, out_order, activities):
        if (self._restricted_edge_type == 'blue'):
            if (place.num_input_trans > 1):
                return list()
        
        child_places = list()
        max_output_activity = max_element(activities, place.output_trans, out_order)
        higher_ordered_activities = out_order.is_larger_relations[max_output_activity]
        for a in higher_ordered_activities:
            new_output_trans = copy.copy(place.output_trans)
            new_output_trans = new_output_trans | a
            num_output_trans = copy.copy(place.num_output_trans) + 1
            child_places.append(Place(copy.copy(place.input_trans), new_output_trans, copy.copy(place.num_input_trans), num_output_trans))
        return child_places

class RefinementSearch(SearchStrategy):

    def __init__(self, miner_factory, restricted_edge_type='blue'):
        self._miner_factory = miner_factory
        self._restricted_edge_type = restricted_edge_type

    def execute(self, log, key, tau, pre_pruning_strategy, in_order, out_order, activities, logger=None, stat_logger=None):
        """
        Uses the results from a different mining approach to get a head start
        for our search phase.
        Assume we have a list of places mined by some algorithm (with better complexity),
        then we calculate our roots this way:
        - Use normal root, if there is no fitting place in its subtrees
        - Use fitting place as start, instead of its coresponding root

        1) Discover places using a different mining approach
        2) Calculate coresponding roots of discovered places
        3) Start search at discovered places, and all roots that do not belong to any
           discovered place
        """
        discovered_places = self._execute_mining_approach(log, key, self._miner_factory)
        starting_roots = self._extract_roots(discovered_places, activities, key, pre_pruning_strategy)
        tree_dfs_strategy = TreeDfsStrategy(self._restricted_edge_type)
        log = est_utils.optimize_for_replay(log, key)
        return tree_dfs_strategy.traverse_roots(
            starting_roots, 
            log,
            key,
            tau,
            in_order, 
            out_order,
            pre_pruning_strategy,
            logger=logger, 
            stat_logger=stat_logger
        )

    def _execute_mining_approach(self, log, key, miner_factory):
        net, im, fm = miner_factory.apply(log)
        resulting_places = set()
        for place in net.places:
            if (place.name != 'end' and place.name != 'start'):
                p = eval(place.name)
                resulting_places.add( Place(frozenset(p[0]), frozenset(p[1])) )
        return resulting_places
    
    def _extract_roots(self, discovered_places, activities, key, pre_pruning_strategy):
        used_roots = set()
        for p in discovered_places:
            for a in p.input_trans:
                for b in p.output_trans:
                    used_roots.add( Place(frozenset([a]), frozenset([b])) )
        roots = (TreeDfsStrategy.RootExtractor.get_roots(activities, key, pre_pruning_strategy)).difference(used_roots)
        roots = roots.union(discovered_places)
        return roots

class NoSearchStrategy(SearchStrategy):

    def execute(
        self, 
        log,
        key,
        tau,
        pre_pruning_strategy,
        in_order,
        out_order,
        activities
    ):
        print('Exectued Search')
        return None
