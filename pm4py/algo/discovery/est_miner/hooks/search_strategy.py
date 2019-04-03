import abc

import pm4py.objects.log.util.log as log_util
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.algo.discovery.est_miner.utils.place_fitness import PlaceFitnessEvaluator, PlaceFitness
from pm4py.algo.discovery.est_miner.utils.activity_order import ActivityOrder

class SearchStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(
        self,
        log,
        key,
        parameters,
        pre_pruning_strategy,
        in_order,
        out_order
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
        out_order
    ):
        fitting_places = list()
        roots = self.__get_roots(log, key, pre_pruning_strategy) # list of places
        for root in roots:
            fitting_places.extend( self.__traverse_red_tree(log, tau, root, in_order, out_order, pre_pruning_strategy) )
            fitting_places.extend( self.__traverse_blue_tree(log, tau, root, in_order, out_order, pre_pruning_strategy) )

    def __get_roots(self, log, key, pre_pruning_strategy):
        roots = list()
        activites = log_util.get_event_labels(log, key)
        for a1 in activites:
            for a2 in activites:
                p = Place([a1], [a2])
                if not pre_pruning_strategy.execute(p):
                    roots.append(p)
        return roots
    
    def __get_max_element(self, activties, order):
        a_max = None
        for a in activties:
            if a_max == None:
                a_max = a
            elif a in order.is_larger_relations[a_max].to_set():
                a_max = a
        return a_max
    
    def __traverse_red_tree(
        self,
        log,
        tau,
        root,
        in_order,
        out_order,
        pre_pruning_strategy
    ):
        if len(root.output_trans) != 1: # restrict red edges
            return list()

        if pre_pruning_strategy.execute(root):
            return list()

        if PlaceFitnessEvaluator.evaluate_place_fitness(log, root, tau) == PlaceFitness.OVERFED:
            return list()

        fitting_places = list()
        a_max = self.__get_max_element(root.input_trans, in_order)
        while (in_order.is_larger_relations[a_max].size() > 0):
            extended_input_trans = root.input_trans.append( in_order.is_larger_relations[a_max].pop() )
            new_root = Place(extended_input_trans, root.output_trans)
            fitting_places.extend( self.__traverse_red_tree(log, tau, new_root, in_order, out_order, pre_pruning_strategy) )
            fitting_places.extend( self.__traverse_blue_tree(log, tau, new_root, in_order, out_order, pre_pruning_strategy) )
        return fitting_places

    def __traverse_blue_tree(
        self,
        log,
        tau,
        root,
        in_order,
        out_order,
        pre_pruning_strategy
    ):
        if pre_pruning_strategy.execute(root):
            return list()
        
        if PlaceFitnessEvaluator.evaluate_place_fitness(log, root, tau) == PlaceFitness.UNDERFED:
            return list()

        fitting_places = list()
        a_max = self.__get_max_element(root.input_trans, out_order)
        while (out_order.is_larger_relations[a_max].size() > 0):
            extended_output_trans = root.output_trans.append( out_order.is_larger_relations[a_max].pop() )
            new_root = Place(root.input_trans, extended_output_trans)
            fitting_places.extend( self.__traverse_red_tree(log, tau, new_root, in_order, out_order, pre_pruning_strategy) )
            fitting_places.extend( self.__traverse_blue_tree(log, tau, new_root, in_order, out_order, pre_pruning_strategy) )
        return fitting_places

class NoSearchStrategy(SearchStrategy):

    def execute(
        self, 
        log, 
        parameters,
        pre_pruning_strategy,
        in_order,
        out_order
    ):
        print('Exectued Search')
        return None
