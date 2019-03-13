import abc

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

