import abc

from pm4py.algo.discovery.est_miner.template.est_miner_template import EstMiner

class EstMinerDirector:
    """
    Construct a new version of the EstMiner from the given
    as code description.
    """

    def __init__(self):
        self.__builder = None
    
    def construct(self, builder):
        self.__builder = builder
        self.__builder.build_pre_processing()
        self.__builder.build_order_calculation()
        self.__builder.build_pre_pruning()
        self.__builder.build_search_strategy()
        self.__builder.build_post_processing()

class EstMinerBuilder(metaclass=abc.ABCMeta):
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
    def build_pre_processing(self):
        pass
    
    @abc.abstractmethod
    def build_order_calculation(self):
        pass
    
    @abc.abstractmethod
    def build_pre_pruning(self):
        pass
    
    @abc.abstractmethod
    def build_search_strategy(self):
        pass
    
    @abc.abstractmethod
    def build_post_processing(self):
        pass
    