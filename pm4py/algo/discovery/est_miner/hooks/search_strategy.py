import abc

class SearchStrategy(abc.ABCMeta):

    @abc.abstractmethod
    def execute(
        self, 
        log, 
        parameters, 
        start_activities, 
        end_activities,
        pre_pruning_strategy,
        in_order,
        out_order
    ):
        pass
