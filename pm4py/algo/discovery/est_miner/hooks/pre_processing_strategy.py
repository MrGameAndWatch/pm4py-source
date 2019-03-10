import abc

class PreProcessingStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def execute(self, log):
        pass