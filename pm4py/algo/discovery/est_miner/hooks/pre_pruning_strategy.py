import abc

import pm4py.algo.discovery.est_miner.utils.constants as const

class PrePruningStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(self, candidate_place):
        """
        Evaluate if the given candidate place is already
        pruned.
        """
        pass

class NoPrePruningStrategy(PrePruningStrategy):

    def execute(self, candidate_place):
        print('Executed Pre Pruning')
        return False

class PrePruneUselessPlacesStrategy:

    def execute(self, candidate_place):
        return (
            const.END_ACTIVITY in candidate_place.input_trans 
            or const.START_ACTIVITY in candidate_place.output_trans 
        )
