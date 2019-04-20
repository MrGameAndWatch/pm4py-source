import time

from pm4py.algo.discovery.est_miner.utils import est_utils
from pm4py.algo.discovery.est_miner.utils import constants as const
import pm4py.objects.log.util.log as log_util
from pm4py.objects import petri
from pm4py.objects.petri.petrinet import Marking
from pm4py.objects.petri.petrinet import PetriNet

from experiments.logging.logger import RuntimeStatisticsLogger

class EstMiner:

    def __init__(self):
        self._name = None
        self._pre_processing_strategy = None
        self._order_calculation_strategy = None
        self._pre_pruning_strategy = None
        self._search_strategy = None
        self._post_processing_strategy = None
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
    @property
    def pre_processing_strategy(self):
        return self._pre_processing_strategy
    
    @pre_processing_strategy.setter
    def pre_processing_strategy(self, strategy):
        self._pre_processing_strategy = strategy
    
    @property
    def order_calculation_strategy(self):
        return self._order_calculation_strategy

    @order_calculation_strategy.setter
    def order_calculation_strategy(self, strategy):
        self._order_calculation_strategy = strategy
    
    @property
    def pre_pruning_strategy(self):
        return self._pre_pruning_strategy

    @pre_pruning_strategy.setter
    def pre_pruning_strategy(self, strategy):
        self._pre_pruning_strategy = strategy
    
    @property
    def search_strategy(self):
        return self._search_strategy

    @search_strategy.setter
    def search_strategy(self, strategy):
        self._search_strategy = strategy
    
    @property
    def post_processing_strategy(self):
        return self._post_processing_strategy

    @post_processing_strategy.setter
    def post_processing_strategy(self, strategy):
        self._post_processing_strategy = strategy

    def apply(self, log, parameters=None, logger=None):
        """
        This method executes the current version of the est miner configured
        through the builder pattern [1].

        Paramters:
        ----------
        log: :class:`pm4py.log.log.EventLog`
            Event log to use in the est-miner
        parameters:
            Parameters for the algorithm:
                - tau: Noise filtering technique (see paper)
        Returns
        -------
        net: :class:`pm4py.entities.petri.petrinet.PetriNet`
        A Petri net describing the event log that is provided as an input
        initial marking: :class:`pm4py.models.net.Marking`
        marking object representing the initial marking
        final marking: :class:`pm4py.models.net.Marking`
        marking object representing the final marking, not guaranteed that it is actually reachable!

        References
        ----------
        Lisa L. Mannel, Wil M. P. van der Aalst, "Finding Complex Process-Structures by Exploiting
        the Token-Game"
        """
        self._ready_for_execution_invariant()
        log = self.pre_processing_strategy.execute(log)
        log = est_utils.insert_unique_start_and_end_activity(log)
        transitions = log_util.get_event_labels(log, parameters['key'])
        in_order, out_order = self.order_calculation_strategy.execute(log, parameters['key'])
        stat_logger = RuntimeStatisticsLogger(self.name, transitions, in_order, out_order)
        stat_logger.algo_started()
        stat_logger.search_started()
        candidate_places = self.search_strategy.execute(
            log=log,
            key=parameters['key'],
            tau=parameters['tau'],
            pre_pruning_strategy=self.pre_pruning_strategy,
            in_order=in_order,
            out_order=out_order,
            logger=logger,
            stat_logger=stat_logger
        )
        stat_logger.search_finished()
        stat_logger.post_processing_started()
        resulting_places = self.post_processing_strategy.execute(
            candidate_places, 
            transitions, 
            logger=logger
        )
        stat_logger.post_processing_finished()
        stat_logger.algo_finished()
        net, src, sink = self._construct_net(log, transitions, resulting_places)
        return net, Marking({src: 1}), Marking({sink: 1}), stat_logger

    def _construct_net(self, log, transitions, resulting_places):
        transition_dict = dict()
        net = PetriNet('est_miner_net' + str(time.time()))
        for i in range(0, len(transitions)):
            transition_dict[transitions[i]] = PetriNet.Transition(transitions[i], transitions[i])
            net.transitions.add(transition_dict[transitions[i]])
        
        source = PetriNet.Place('start')
        net.places.add(source)
        petri.utils.add_arc_from_to(source, transition_dict[const.START_ACTIVITY], net)

        sink = PetriNet.Place('end')
        net.places.add(sink)
        petri.utils.add_arc_from_to(transition_dict[const.END_ACTIVITY], sink, net)

        for p in resulting_places:
            place = PetriNet.Place(p.name)
            net.places.add(place)
            for in_trans in p.input_trans:
                petri.utils.add_arc_from_to(transition_dict[in_trans], place, net)
            for out_trans in p.output_trans:
                petri.utils.add_arc_from_to(place, transition_dict[out_trans], net)
        return net, source, sink
    
    def _ready_for_execution_invariant(self):
        assert(self.name is not None)
        assert(self.pre_processing_strategy is not None)
        assert(self.order_calculation_strategy is not None)
        assert(self.pre_pruning_strategy is not None)
        assert(self.search_strategy is not None)
        assert(self.post_processing_strategy is not None)
