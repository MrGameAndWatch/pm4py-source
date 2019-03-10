import abc

class OrderCalculationStrategy(abc.ABCMeta):

    @abc.abstractmethod
    def execute(self, log):
        pass
