import abc

class SearchStrategy(abc.ABCMeta):

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
        pass
