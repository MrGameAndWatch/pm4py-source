import abc

from pm4py.algo.discovery.alpha import factory as alpha_factory
from pm4py.algo.discovery.est_miner.template.est_miner_template import EstMiner
from pm4py.algo.discovery.est_miner.hooks.pre_processing_strategy import NoPreProcessingStrategy

from pm4py.algo.discovery.est_miner.hooks.order_calculation_strategy \
import NoOrderCalculationStrategy, LexicographicalOrderStrategy, MaxUnderfedPlacesThroughAbsTraceFreqOrderStrategy, \
MaxUnderfedPlacesThroughRelativeTraceFreqOrderStrategy, MaxOverfedPlacesThroughAbsTraceFreqOrderStrategy, \
MaxOverfedPlacesThroughRelativeTraceFreqOrderStrategy

from pm4py.algo.discovery.est_miner.hooks.search_strategy \
import NoSearchStrategy, TreeDfsStrategy, RefinementSearch

from pm4py.algo.discovery.est_miner.hooks.post_processing_strategy \
import NoPostProcessingStrategy, DeleteDuplicatePlacesPostProcessingStrategy, \
RemoveRedundantPlacesLPPostProcessingStrategy, RemoveRedundantAndImplicitPlacesPostProcessingStrategy, \
RemoveImplicitPlacesLPPostProcessingStrategy, RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy

from pm4py.algo.discovery.est_miner.hooks.pre_pruning_strategy \
import NoPrePruningStrategy, PrePruneUselessPlacesStrategy, HeuristicPrePrune, ImportantPlacesPrePruning

class EstMinerDirector:
    """
    Construct a new version of the EstMiner from the given
    as code description.
    """

    def __init__(self):
        self._builder = None
    
    def construct(self, builder):
        self._builder = builder
        self._builder.build_name()
        self._builder.build_pre_processing_strategy()
        self._builder.build_order_calculation_strategy()
        self._builder.build_pre_pruning_strategy()
        self._builder.build_search_strategy()
        self._builder.build_post_processing_strategy()

class EstMinerBuilder(abc.ABC):
    """
    Interface for defining how to construct different versions 
    of the EstMiner.
    """

    def __init__(self):
        self._est_miner = EstMiner()
    
    @property
    def est_miner(self):
        return self._est_miner

    @abc.abstractmethod
    def build_name(self):
        pass
    
    @abc.abstractmethod
    def build_pre_processing_strategy(self):
        pass
    
    @abc.abstractmethod
    def build_order_calculation_strategy(self):
        pass
    
    @abc.abstractmethod
    def build_pre_pruning_strategy(self):
        pass
    
    @abc.abstractmethod
    def build_search_strategy(self):
        pass
    
    @abc.abstractmethod
    def build_post_processing_strategy(self):
        pass
    

class TestEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'TestEstMiner'

    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()
    
    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = NoOrderCalculationStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = NoPrePruningStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = NoSearchStrategy()
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = NoPostProcessingStrategy()

class StandardEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'OriginalPaperEstMiner'

    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()

    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = LexicographicalOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = PrePruneUselessPlacesStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = TreeDfsStrategy(restricted_edge_type='red')
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()

class MaxCutoffsAbsFreqEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'MaxCutoffsAbsFreq'

    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()

    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = MaxUnderfedPlacesThroughAbsTraceFreqOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = PrePruneUselessPlacesStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = TreeDfsStrategy(restricted_edge_type='red')
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()

class MaxCutoffsRelTraceFreqEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'MaxCutoffsRelTraceFreq'
    
    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()

    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = MaxUnderfedPlacesThroughRelativeTraceFreqOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = PrePruneUselessPlacesStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = TreeDfsStrategy(restricted_edge_type='red')
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()

class RestrictBlueEdgesAndMaxCutoffsAbsTraceFreqEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'RestrictBlueEdgesAndMaxCutoffsRelTraceFreq'
    
    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()
    
    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = MaxOverfedPlacesThroughAbsTraceFreqOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = PrePruneUselessPlacesStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = TreeDfsStrategy(restricted_edge_type='blue')
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()

class MaxCutoffsRelTraceFreqHeuristicPruningEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'MaxCutoffsRelTraceFreqHeuristicPruning'
    
    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()

    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = MaxUnderfedPlacesThroughRelativeTraceFreqOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = HeuristicPrePrune()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = TreeDfsStrategy(restricted_edge_type='red')
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()

class AlphaMinerRefinementSearchEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'AlphaMinerRefinementSearch'
    
    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()

    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = MaxUnderfedPlacesThroughAbsTraceFreqOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = PrePruneUselessPlacesStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = RefinementSearch(alpha_factory)
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()

class PlaceInterestPrePruningRestrictRedEdgesEstMinerBuilder(EstMinerBuilder):

    def build_name(self):
        self.est_miner.name = 'PlaceInterestPrePruningRestrictRedEdges'
    
    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()
    
    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = MaxUnderfedPlacesThroughRelativeTraceFreqOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = ImportantPlacesPrePruning()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = TreeDfsStrategy(restricted_edge_type='red')
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy()
