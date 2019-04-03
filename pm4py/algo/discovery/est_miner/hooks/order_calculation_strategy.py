import abc

import pm4py.objects.log.util.log as log_util
from pm4py.algo.discovery.est_miner.utils.activity_order import ActivityOrder, \
ActivityOrderBuilder

class OrderCalculationStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(self, log, key):
        """
        Calculate two orders on the given log, one for 
        input and one for out activities.

        Parameters:
        -------------
        log: :class:`pm4py.log.log.EventLog The event log

        Returns:
        -------------
        input_order: :class:ActivityOrder - ordering on input activities
        output_order: :class:ActivityOrder - ordering on output activities
        """
        pass

class NoOrderCalculationStrategy(OrderCalculationStrategy):

    def execute(self, log):
        print('Executed Order Calculation')
        return None, None

class LexicographicalOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        activites = log_util.get_event_labels(log, key)
        input_order_builder  = ActivityOrderBuilder()
        output_order_builder = ActivityOrderBuilder()

        sorted_activities = sorted(activites, key=str.lower)
        for i in range(0, len(sorted_activities)):
            for j in range(i, len(sorted_activities)):
                input_order_builder.add_relation(larger=sorted_activities[j], smaller=sorted_activities[i])
                output_order_builder.add_relation(larger=sorted_activities[j], smaller=sorted_activities[i])
        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())
