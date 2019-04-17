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

class MaxCutoffsThroughRelativeTraceFreqOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        """
        A place is more likely to be overfed, if its' input transitions
        are more likely to occur in a trace, than the place's output
        transitions.

        A place is more likely to be underfed, if its' output transitions
        are more likely to occur in a trace, than the place's input transitons.
        """
        rel_trace_occ = {}
        activities = log_util.get_event_labels(log, key)
        for a in activities:
            traces = 0
            for t in log:
                occ = False
                for e in t:
                    if a == e[key]:
                        occ = True
                if occ:
                    traces += 1
            rel_trace_occ[a] = traces / len(log)
        print(rel_trace_occ)
        
        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_rel_trace_occ = sorted(rel_trace_occ.items(), key=lambda x: x[1])
        for i in range(0, len(sorted_rel_trace_occ)):
            selection = slice(i + 1, len(sorted_rel_trace_occ), 1)
            larger_elements_smallest_first = sorted_rel_trace_occ[selection]
            larger_elements_largest_first  = sorted_rel_trace_occ[selection][::-1]
            smaller_a = sorted_rel_trace_occ[i][0]
            if (larger_elements_largest_first is not None):
                for (larger_a, freq) in larger_elements_largest_first:
                    input_order_builder.add_relation(larger=smaller_a, smaller=larger_a)
                for (larger_a, freq) in larger_elements_smallest_first:
                    output_order_builder.add_relation(larger=smaller_a, smaller=larger_a)
        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())
    
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
            larger_elements_smallest_first = sorted_activities[selection]
            larger_elements_largest_first  = sorted_activities[selection][::-1]
            smaller_a = sorted_activities[i][0]
            if (larger_elements_largest_first is not None):
                for (larger_a, freq) in larger_elements_largest_first:
                    input_order_builder.add_relation(larger=smaller_a, smaller=larger_a)
                for (larger_a, freq) in larger_elements_smallest_first:
                    output_order_builder.add_relation(larger=smaller_a, smaller=larger_a)
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
