import abc

from pm4py.algo.discovery.est_miner.template.est_miner_template import EstMiner
from pm4py.algo.discovery.est_miner.hooks.pre_processing_strategy import NoPreProcessingStrategy
from pm4py.algo.discovery.est_miner.hooks.order_calculation_strategy \
import NoOrderCalculationStrategy, LexicographicalOrderStrategy
from pm4py.algo.discovery.est_miner.hooks.search_strategy \
import NoSearchStrategy, RestrictedRedTreeDfsStrategy
from pm4py.algo.discovery.est_miner.hooks.post_processing_strategy \
import NoPostProcessingStrategy, DeleteDuplicatePlacesPostProcessingStrategy
from pm4py.algo.discovery.est_miner.hooks.pre_pruning_strategy \
import NoPrePruningStrategy, PrePruneUselessPlacesStrategy

class EstMinerDirector:
    """
    Construct a new version of the EstMiner from the given
    as code description.
    """

    def __init__(self):
        self.__builder = None
    
    def construct(self, builder):
        self.__builder = builder
        self.__builder.build_pre_processing_strategy()
        self.__builder.build_order_calculation_strategy()
        self.__builder.build_pre_pruning_strategy()
        self.__builder.build_search_strategy()
        self.__builder.build_post_processing_strategy()

class EstMinerBuilder(abc.ABC):
    """
    Interface for defining how to construct different versions 
    of the EstMiner.
    """

    def __init__(self):
        self.__est_miner = EstMiner()
    
    @property
    def est_miner(self):
        return self.__est_miner
    
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

    def build_pre_processing_strategy(self):
        self.est_miner.pre_processing_strategy = NoPreProcessingStrategy()

    def build_order_calculation_strategy(self):
        self.est_miner.order_calculation_strategy = LexicographicalOrderStrategy()
    
    def build_pre_pruning_strategy(self):
        self.est_miner.pre_pruning_strategy = PrePruneUselessPlacesStrategy()
    
    def build_search_strategy(self):
        self.est_miner.search_strategy = RestrictedRedTreeDfsStrategy()
    
    def build_post_processing_strategy(self):
        self.est_miner.post_processing_strategy = DeleteDuplicatePlacesPostProcessingStrategy()
