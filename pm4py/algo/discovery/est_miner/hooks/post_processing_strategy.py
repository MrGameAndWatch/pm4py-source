import abc

class PostProcessingStrategy(abc.ABCMeta):

    @abc.abstractmethod
    def execute(self, candidate_places):
        pass
