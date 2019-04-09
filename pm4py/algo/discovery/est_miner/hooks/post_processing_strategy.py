import abc

class PostProcessingStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(self, candidate_places):
        """
        Remove redundant places from the found candidate places
        to make the resulting network better interpretable by 
        human readers.
        """
        pass

class NoPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places):
        print('Executed Post Processing')
        return candidate_places

class DeleteDuplicatePlacesPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places):
        return set(candidate_places)

class ReplayBasedPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places):
        # Create net
        # for each place
        # remove place
        # test if net still replays log
        # if yes: keep place removed
        # if no: re-add place
        return candidate_places
