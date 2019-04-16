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

class TraceFrequenciesOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        """
        For each activity get trace-frequency (#traces 
        the activity occurrs in) in log. Sort them based on their
        frequencies: Highest occurring element comes first (often occurrs).
        --> Could under or overfeed for many traces.
        """
        activities = log_util.get_event_labels(log, key)
        trace_freq = self._get_trace_freq(activities, log, key)

        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_activities = sorted(trace_freq.items(), key=lambda x: x[1])
        for i in range(0, len(sorted_activities)):
            selection = slice(i+1, len(sorted_activities), 1)
            larger_elements = sorted_activities[selection][::-1]
            smaller_a = sorted_activities[i][0]
            if (larger_elements is not None):
                for (larger_a, freq) in larger_elements:
                    input_order_builder.add_relation(larger=larger_a, smaller=smaller_a)
                    output_order_builder.add_relation(larger=larger_a, smaller=smaller_a)
        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

    def _get_trace_freq(self, activites, log, key):
        freq = {}
        for a in activites:
            freq[a] = 0
        for trace in log:
            for e in trace:
                freq[e[key]] += 1
        return freq

class LexicographicalOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        activites = log_util.get_event_labels(log, key)
        input_order_builder  = ActivityOrderBuilder(activites)
        output_order_builder = ActivityOrderBuilder(activites)

        sorted_activities = sorted(activites, key=str.lower)
        for i in range(0, len(sorted_activities)):
            for j in range(i, len(sorted_activities)):
                if (sorted_activities[i] != sorted_activities[j]):
                    input_order_builder.add_relation(larger=sorted_activities[j], smaller=sorted_activities[i])
                    output_order_builder.add_relation(larger=sorted_activities[j], smaller=sorted_activities[i])
        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())
