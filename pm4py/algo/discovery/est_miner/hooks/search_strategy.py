import abc
import copy
import logging

import pm4py.objects.log.util.log as log_util
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.algo.discovery.est_miner.utils.place_fitness import PlaceFitnessEvaluator, PlaceFitness
from pm4py.algo.discovery.est_miner.utils.activity_order import ActivityOrder, max_element, min_element

class SearchStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(
        self,
        log,
        key,
        tau,
        pre_pruning_strategy,
        in_order,
        out_order,
        logger=None,
        stat_logger=None
    ):
        """
        Strategy how to search through the candidate space,
        when to cut off search and where to start and finish.
        """
        pass

class RestrictedRedTreeDfsStrategy(SearchStrategy):

    def execute(
        self,
        log,
        key,
        tau,
        pre_pruning_strategy,
        in_order,
        out_order,
        logger=None,
        stat_logger=None
    ):
        if (logger is not None):
            logger.info('Starting Search')
        fitting_places = list()
        roots = self._get_roots(log, key, pre_pruning_strategy) # list of places
        for root in roots:
            fitting_places.extend( self._traverse_red_tree(log, tau, key, root, in_order, out_order, pre_pruning_strategy, logger=logger, stat_logger=stat_logger) )
            fitting_places.extend( self._traverse_blue_tree(log, tau, key, root, in_order, out_order, pre_pruning_strategy, logger=logger, stat_logger=stat_logger) )
        return fitting_places

    def _get_roots(self, log, key, pre_pruning_strategy):
        roots = list()
        activites = log_util.get_event_labels(log, key)
        for a1 in activites:
            for a2 in activites:
                p = Place(frozenset([a1]), frozenset([a2]))
                if not pre_pruning_strategy.execute(p):
                    roots.append(p)
        return roots
    
    def _traverse_red_tree(
        self,
        log,
        tau,
        key,
        root,
        in_order,
        out_order,
        pre_pruning_strategy,
        logger=None,
        stat_logger=None
    ):
        if pre_pruning_strategy.execute(root):
            return list()

        if len(root.output_trans) != 1: # restrict red edges
            return list()

        if(stat_logger is not None):
            stat_logger.replay_started()
        place_fitness_states = PlaceFitnessEvaluator.evaluate_place_fitness(log, root, tau, key)
        if(stat_logger is not None):
            stat_logger.replay_finished()

        fitting_places = list()
        if PlaceFitness.FITTING in place_fitness_states:
            if (logger is not None):
                logger.info('Fitting: ' + root.name)
            fitting_places.append(root)
        
        if PlaceFitness.OVERFED in place_fitness_states: # prune
            if (logger is not None):
                logger.info('Pruned (Red): ' + root.name)
            if (stat_logger is not None):
                stat_logger.pruned_red_place(root)
            return fitting_places

        a_max = max_element(root.input_trans, in_order)
        larger_elements = copy.copy(out_order.is_larger_relations[a_max])
        while (len(larger_elements) > 0):
            extended_input_trans = list(root.input_trans.copy())
            new_element = larger_elements.pop()
            if new_element in extended_input_trans:
                continue
            extended_input_trans.append( new_element )
            input_trans = frozenset(extended_input_trans)
            new_root = Place(input_trans, root.output_trans.copy())
            fitting_places.extend( self._traverse_red_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy, logger=logger, stat_logger=stat_logger) )
            fitting_places.extend( self._traverse_blue_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy, logger=logger, stat_logger=stat_logger) )
        return fitting_places

    def _traverse_blue_tree(
        self,
        log,
        tau,
        key,
        root,
        in_order,
        out_order,
        pre_pruning_strategy,
        logger=None,
        stat_logger=None
    ):
        if pre_pruning_strategy.execute(root):
            return list()
        
        if(stat_logger is not None):
            stat_logger.replay_started()
        place_fitness_states = PlaceFitnessEvaluator.evaluate_place_fitness(log, root, tau, key)
        if (stat_logger is not None):
            stat_logger.replay_finished()

        fitting_places = list()
        if PlaceFitness.FITTING in place_fitness_states:
            if (logger is not None):
                logger.info('Fitting: ' + root.name)
            fitting_places.append(root)

        if PlaceFitness.UNDERFED in place_fitness_states: # prune
            if (logger is not None):
                logger.info('Pruned (Blue): ' + root.name)
            
            if (stat_logger is not None):
                stat_logger.pruned_blue_place(root)
            return fitting_places 

        a_max = max_element(root.output_trans, out_order)
        larger_elements = copy.copy(out_order.is_larger_relations[a_max])
        while (len(larger_elements) > 0):
            extended_output_trans = list(root.output_trans.copy())
            new_element = larger_elements.pop()
            if new_element in extended_output_trans:
                continue
            extended_output_trans.append(new_element)
            output_trans = frozenset(extended_output_trans)
            new_root = Place(root.input_trans.copy(), output_trans)
            fitting_places.extend( self._traverse_red_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy, logger=logger, stat_logger=stat_logger) )
            fitting_places.extend( self._traverse_blue_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy, logger=logger, stat_logger=stat_logger) )
        return fitting_places

class NoSearchStrategy(SearchStrategy):

    def execute(
        self, 
        log,
        key,
        tau,
        pre_pruning_strategy,
        in_order,
        out_order
    ):
        print('Exectued Search')
        return None
