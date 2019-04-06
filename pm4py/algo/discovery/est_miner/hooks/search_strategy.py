import abc
import copy

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
        tau,
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
            fitting_places.extend( self.__traverse_red_tree(log, tau, key, root, in_order, out_order, pre_pruning_strategy) )
            fitting_places.extend( self.__traverse_blue_tree(log, tau, key, root, in_order, out_order, pre_pruning_strategy) )
        return fitting_places

    def __get_roots(self, log, key, pre_pruning_strategy):
        roots = list()
        activites = log_util.get_event_labels(log, key)
        for a1 in activites:
            for a2 in activites:
                p = Place({a1}, {a2})
                if not pre_pruning_strategy.execute(p):
                    roots.append(p)
        return roots
    
    def __get_max_element(self, activties, order):
        a_max = None
        for a in activties:
            if a_max == None:
                a_max = a
            elif a in set(order.is_larger_relations[a_max]):
                a_max = a
        return a_max
    
    def __traverse_red_tree(
        self,
        log,
        tau,
        key,
        root,
        in_order,
        out_order,
        pre_pruning_strategy
    ):
        if pre_pruning_strategy.execute(root):
            return list()

        if len(root.output_trans) != 1: # restrict red edges
            return list()

        place_fitness_states = PlaceFitnessEvaluator.evaluate_place_fitness(log, root, tau, key)
        fitting_places = list()
        if PlaceFitness.FITTING in place_fitness_states:
            fitting_places.append(root)
        
        if PlaceFitness.OVERFED in place_fitness_states:
            return fitting_places

        a_max = self.__get_max_element(root.input_trans, in_order)
        larger_elements = copy.copy(out_order.is_larger_relations[a_max])
        while (len(larger_elements) > 0):
            extended_input_trans = copy.copy(root.input_trans)
            new_element = larger_elements.pop()
            if new_element in extended_input_trans:
                continue
            extended_input_trans.add( new_element )
            new_root = Place(extended_input_trans, copy.copy(root.output_trans))
            fitting_places.extend( self.__traverse_red_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy) )
            fitting_places.extend( self.__traverse_blue_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy) )
        return fitting_places

    def __traverse_blue_tree(
        self,
        log,
        tau,
        key,
        root,
        in_order,
        out_order,
        pre_pruning_strategy
    ):
        if pre_pruning_strategy.execute(root):
            return list()
        
        place_fitness_states = PlaceFitnessEvaluator.evaluate_place_fitness(log, root, tau, key)
        fitting_places = list()
        if PlaceFitness.FITTING in place_fitness_states:
            fitting_places.append(root)

        if PlaceFitness.UNDERFED in place_fitness_states:
            return fitting_places 

        a_max = self.__get_max_element(root.input_trans, out_order)
        larger_elements = copy.copy(out_order.is_larger_relations[a_max])
        while (len(larger_elements) > 0):
            extended_output_trans = copy.copy(root.output_trans)
            new_element = larger_elements.pop()
            if new_element in extended_output_trans:
                continue
            extended_output_trans.add(new_element)
            new_root = Place(copy.copy(root.input_trans), extended_output_trans)
            fitting_places.extend( self.__traverse_red_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy) )
            fitting_places.extend( self.__traverse_blue_tree(log, tau, key, new_root, in_order, out_order, pre_pruning_strategy) )
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
