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
from pm4py.algo.discovery.est_miner.utils.constants import ParameterNames

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
        heuristic_parameters=None,
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
        def get_roots(cls, activities, pre_pruning_strategy, heuristic_parameters=None):
            roots = set()
            for a1 in activities:
                for a2 in activities:
                    p = Place(a1, a2, 1, 1)
                    if not pre_pruning_strategy.execute(p, parameters=heuristic_parameters):
                        roots.add(p)
            return roots
    
    def __init__(self, restricted_edge_type):
        assert(restricted_edge_type == 'red' or restricted_edge_type == 'blue')
        self._restricted_edge_type = restricted_edge_type
    
    def execute(
        self, 
        log, 
        tau, 
        pre_pruning_strategy, 
        in_order, 
        out_order, 
        activities, 
        heuristic_parameters=None, 
        logger=None, 
        stat_logger=None
    ):
        if (logger is not None):
            logger.info('Starting Search')
        roots = self.RootExtractor.get_roots(activities, pre_pruning_strategy, heuristic_parameters=heuristic_parameters)
        return self.traverse_roots(
            roots,
            log,
            tau,
            in_order,
            out_order,
            pre_pruning_strategy,
            activities,
            heuristic_parameters=heuristic_parameters,
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
        heuristic_parameters=None,
        logger=None,
        stat_logger=None
    ):
        fitting_places = list()
        args = list()
        for root in roots:
            fitting_places.extend(self._traverse_place(log, tau, root, in_order, out_order, pre_pruning_strategy, activities, heuristic_parameters=heuristic_parameters))#, logger=logger, stat_logger=stat_logger))
            #args.append( (log, tau, root, in_order, out_order, pre_pruning_strategy, activities, heuristic_parameters) )
        #with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        #    fitting_places = pool.starmap(self._traverse_place, args)
        
        #flat_result = [p for fitting in fitting_places for p in fitting]
        #return flat_result
        return fitting_places
    
    def _traverse_place(
        self,
        log,
        tau,
        place,
        in_order,
        out_order,
        pre_pruning_strategy,
        activities,
        heuristic_parameters=None,
        logger=None,
        stat_logger=None
    ):
        if logger is not None:
            logger.info('Checking node ' + place.name)
        
        if pre_pruning_strategy.execute(place, parameters=heuristic_parameters):
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
            if self._can_replay_important_traces(
                place,
                fitting_places,
                heuristic_parameters[ParameterNames.IMPORTANT_TRACES],
                heuristic_parameters[ParameterNames.ACTIVITIES],
                heuristic_parameters[ParameterNames.START_ACTIVITY],
                heuristic_parameters[ParameterNames.END_ACTIVITY]
            ):
                fitting_places.append(place)
            heuristic_parameters[ParameterNames.FITTING_PLACES].append(place)
        
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
                heuristic_parameters=heuristic_parameters,
                logger=logger,
                stat_logger=stat_logger
            ))
        return fitting_places
    
    def _can_replay_important_traces(
        self,
        place,
        fitting_places,
        important_traces,
        activities,
        start_activity,
        end_activity
    ):
        places = fitting_places.copy()
        places.append(place)
        activity_as_input = dict()
        activity_as_output = dict()
        for activity in activities:
            activity_as_input[activity] = list()
            activity_as_output[activity] = list()

        for p in places:
            for activity in activities:
                if (activity & p.input_trans) != 0:
                    activity_as_input[activity].append(p)
                if (activity & p.output_trans) != 0:
                    activity_as_output[activity].append(p)
        start_place = Place(0, start_activity, 0, 1)
        sink_place = Place(end_activity, 0, 1, 0)
        activity_as_output[start_activity].append(start_place)
        activity_as_input[end_activity].append(sink_place)
        places.append(start_place)
        places.append(sink_place)

        for trace in important_traces:
            if not self._can_replay_trace(
                trace,
                activities,
                places,
                activity_as_input,
                activity_as_output,
                start_place,
                sink_place
            ):
                return False
        return True
    
    def _can_replay_trace(
        self,
        trace,
        activities,
        places,
        activity_as_input,
        activity_as_output,
        start_place,
        sink_place
    ):
        token_map = dict()
        for place in places:
            if place == start_place:
                token_map[place] = 1
            else:
                token_map[place] = 0

        # check if all events can be executed in order
        for event in trace:
            for place in activity_as_output[event]:
                if token_map[place] <= 0:
                    return False
                else:
                    token_map[place] -= 1
            for place in activity_as_input[event]:
                token_map[place] += 1

        # check if final marking is reached
        for place in places:
            if place == sink_place:
                if token_map[place] != 1:
                    return False
            else:
                if token_map[place] != 0:
                    return False

        return True
    
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

# class RefinementSearch(SearchStrategy):

#     def __init__(self, miner_factory, restricted_edge_type='blue'):
#         self._miner_factory = miner_factory
#         self._restricted_edge_type = restricted_edge_type

#     def execute(self, log, key, tau, pre_pruning_strategy, in_order, out_order, activities, heuristic_parameters=None, logger=None, stat_logger=None):
#         """
#         Uses the results from a different mining approach to get a head start
#         for our search phase.
#         Assume we have a list of places mined by some algorithm (with better complexity),
#         then we calculate our roots this way:
#         - Use normal root, if there is no fitting place in its subtrees
#         - Use fitting place as start, instead of its coresponding root

#         1) Discover places using a different mining approach
#         2) Calculate coresponding roots of discovered places
#         3) Start search at discovered places, and all roots that do not belong to any
#            discovered place
#         """
#         discovered_places = self._execute_mining_approach(log, key, self._miner_factory)
#         starting_roots = self._extract_roots(discovered_places, activities, key, pre_pruning_strategy)
#         tree_dfs_strategy = TreeDfsStrategy(self._restricted_edge_type)
#         log = est_utils.optimize_for_replay(log, key)
#         return tree_dfs_strategy.traverse_roots(
#             starting_roots, 
#             log,
#             key,
#             tau,
#             in_order, 
#             out_order,
#             pre_pruning_strategy,
#             heuristic_parameters=heuristic_parameters,
#             logger=logger, 
#             stat_logger=stat_logger
#         )

#     def _execute_mining_approach(self, log, key, miner_factory):
#         net, im, fm = miner_factory.apply(log)
#         resulting_places = set()
#         for place in net.places:
#             if (place.name != 'end' and place.name != 'start'):
#                 p = eval(place.name)
#                 resulting_places.add( Place(frozenset(p[0]), frozenset(p[1])) )
#         return resulting_places
    
#     def _extract_roots(self, discovered_places, activities, key, pre_pruning_strategy):
#         used_roots = set()
#         for p in discovered_places:
#             for a in p.input_trans:
#                 for b in p.output_trans:
#                     used_roots.add( Place(frozenset([a]), frozenset([b])) )
#         roots = (TreeDfsStrategy.RootExtractor.get_roots(activities, key, pre_pruning_strategy)).difference(used_roots)
#         roots = roots.union(discovered_places)
#         return roots

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
