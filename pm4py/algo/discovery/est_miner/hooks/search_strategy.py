import abc

class SearchStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(
        self, 
        log, 
        parameters, 
        start_activity, 
        end_activity,
        pre_pruning_strategy,
        in_order,
        out_order
    ):
        """
        Strategy how to search through the candidate space,
        when to cut off search and where to start and finish.
        """
        pass

class NoSearchStrategy(SearchStrategy):

    def execute(
        self, 
        log, 
        parameters, 
        start_activity, 
        end_activity,
        pre_pruning_strategy,
        in_order,
        out_order
    ):
        print('Exectued Search')
        return None
