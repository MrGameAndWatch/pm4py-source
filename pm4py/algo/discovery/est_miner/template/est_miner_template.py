from pm4py.algo.discovery.est_miner.utils import est_utils
from pm4py.objects.petri.petrinet import Marking

class EstMiner:

    def __init__(self):
        self.__pre_processing_strategy = None
        self.__order_calculation_strategy = None
        self.__pre_pruning_strategy = None
        self.__search_strategy = None
        self.__post_processing_strategy = None
    
    @property
    def pre_processing_strategy(self):
        return self.__pre_processing_strategy
    
    @pre_processing_strategy.setter
    def pre_processing_strategy(self, strategy):
        self.__pre_processing_strategy = strategy
    
    @property
    def order_calculation_strategy(self):
        return self.__order_calculation_strategy

    @order_calculation_strategy.setter
    def order_calculation_strategy(self, strategy):
        self.__order_calculation_strategy = strategy
    
    @property
    def pre_pruning_strategy(self):
        return self.__pre_pruning_strategy

    @pre_pruning_strategy.setter
    def pre_pruning_strategy(self, strategy):
        self.__pre_pruning_strategy = strategy
    
    @property
    def search_strategy(self):
        return self.__search_strategy

    @search_strategy.setter
    def search_strategy(self, strategy):
        self.__search_strategy = strategy
    
    @property
    def post_processing_strategy(self):
        return self.__post_processing_strategy

    @post_processing_strategy.setter
    def post_processing_strategy(self, strategy):
        self.__post_processing_strategy = strategy

    def apply(self, log, parameters=None):
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
        self.__ready_for_execution_invariant()
        log = self.pre_processing_strategy.execute(log)
        log = est_utils.insert_unique_start_and_end_activity(log)
        in_order, out_order = self.order_calculation_strategy.execute(log)
        candidate_places = self.search_strategy.execute(
            log=log,
            parameters=parameters,
            pre_pruning_strategy=self.pre_pruning_strategy,
            in_order=in_order,
            out_order=out_order
        )
        resulting_places = self.post_processing_strategy.execute(candidate_places)
        net, src, sink = self.__construct_net(log, resulting_places)
        return net, Marking({src: 1}), Marking({sink: 1})
        # output net

    def __construct_net(self, log, resulting_places):
        return None, None, None
    
    def __ready_for_execution_invariant(self):
        assert(self.pre_processing_strategy is not None)
        assert(self.order_calculation_strategy is not None)
        assert(self.pre_pruning_strategy is not None)
        assert(self.search_strategy is not None)
        assert(self.post_processing_strategy is not None)
