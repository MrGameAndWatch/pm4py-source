import abc

import pm4py.objects.log.util.log as log_util
from pm4py.algo.discovery.est_miner.utils.activity_order import ActivityOrder, \
ActivityOrderBuilder

def get_abs_trace_occ(log, key, activities):
    abs_trace_occ = {}
    for a in activities:
        traces = 0
        for t in log:
            occ = False
            for e in t:
                if a == e[key]:
                    occ = True
            if occ:
                traces += 1
        abs_trace_occ[a] = traces
    return abs_trace_occ

def get_rel_trace_occ(log, key, activities):
    relative_trace_occ = {}
    for a in activities:
        traces = 0
        for t in log:
            occ = False
            for e in t:
                if a == e[key]:
                    occ = True
            if occ:
                traces += 1
        relative_trace_occ[a] = traces / len(log)
    return relative_trace_occ

def get_avg_trace_occ(log, key, activities):
    avg_trace_occ = {}
    for a in activities:
        avg_occ = 0
        for t in log:
            occ = 0
            for e in t:
                if a == e[key]:
                    occ += 1
            avg_occ += (occ / len(t))
        avg_trace_occ[a] = avg_occ / len(log)
    return avg_trace_occ

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

class MaxOverfedPlacesThroughAvgTraceOccOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        activities = log_util.get_event_labels(log, key)
        avg_trace_occ = get_avg_trace_occ(log, key, activities)

        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_avg_trace_occ = sorted(avg_trace_occ.items(), key=lambda x: x[1])

        for i in reversed(range(len(sorted_avg_trace_occ))):
            for j in reversed(range(i)):
                output_order_builder.add_relation(larger=sorted_avg_trace_occ[j][0], smaller=sorted_avg_trace_occ[i][0])

        for i in range(len(sorted_avg_trace_occ)):
            for j in range(i):
                input_order_builder.add_relation(larger=sorted_avg_trace_occ[j][0], smaller=sorted_avg_trace_occ[i][0])

        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

class MaxOverfedPlacesThroughAbsTraceFreqOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        # A place is more likely to be overfed, if its' input transitions
        # are more likely to occur in a trace, than the place's output
        # transitions.
        activities = log_util.get_event_labels(log, key)
        abs_trace_occ = get_abs_trace_occ(log, key, activities)
        
        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_abs_trace_occ = sorted(abs_trace_occ.items(), key=lambda x: x[1])
        # Build output order
        # most frequent element is minimal
        for i in reversed(range(len(sorted_abs_trace_occ))):
            for j in reversed(range(i)):
                output_order_builder.add_relation(larger=sorted_abs_trace_occ[j][0], smaller=sorted_abs_trace_occ[i][0])
        
        # Build input order
        # least frequent element is minimal
        for i in range(len(sorted_abs_trace_occ)):
            for j in range(i):
                input_order_builder.add_relation(larger=sorted_abs_trace_occ[j][0], smaller=sorted_abs_trace_occ[i][0])

        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

class MaxOverfedPlacesThroughRelativeTraceFreqOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        # A place is more likely to be overfed, if its' input transitions
        # are more likely to occur in a trace, than the place's output
        # transitions.
        activities = log_util.get_event_labels(log, key)
        rel_trace_occ = get_rel_trace_occ(log, key, activities)
        
        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_rel_trace_occ = sorted(rel_trace_occ.items(), key=lambda x: x[1])
        # Build output order
        # most frequent element is minimal
        for i in reversed(range(len(sorted_rel_trace_occ))):
            for j in reversed(range(i)):
                output_order_builder.add_relation(larger=sorted_rel_trace_occ[j][0], smaller=sorted_rel_trace_occ[i][0])
        
        # Build input order
        # least frequent element is minimal
        for i in range(len(sorted_rel_trace_occ)):
            for j in range(i):
                input_order_builder.add_relation(larger=sorted_rel_trace_occ[j][0], smaller=sorted_rel_trace_occ[i][0])

        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

class MaxUnderfedPlacesThroughAFOIOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        activities = log_util.get_event_labels(log, key)
        avg_first_occ_index = self._avg_first_occ_index(log, key, activities)

        input_order_builder = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_avg_first_occ_index = sorted(avg_first_occ_index.items(), key=lambda x: x[1])

        for i in range(len(sorted_avg_first_occ_index)):
            for j in range(i+1, len(sorted_avg_first_occ_index)):
                output_order_builder.add_relation(larger=sorted_avg_first_occ_index[j][0], smaller=sorted_avg_first_occ_index[i][0])
        
        for i in reversed(range(len(sorted_avg_first_occ_index))):
            for j in reversed(range(i)):
                input_order_builder.add_relation(larger=sorted_avg_first_occ_index[j][0], smaller=sorted_avg_first_occ_index[i][0])
        
        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

    def _avg_first_occ_index(self, log, key, activites):
        avg_first_occ_index = dict()
        for a in activites:
            index_sum = 0
            traces = 0
            for t in log:
                occ = False
                index = 0
                for e in t:
                    if a == e[key]:
                        if not occ:
                            index_sum += index
                            occ = True
                    index += 1
                if occ:
                    traces += 1
            avg_first_occ_index[a] = (index_sum / traces)
        return avg_first_occ_index

class MaxUnderfedPlacesThroughAvgTraceOccOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        activities = log_util.get_event_labels(log, key)
        avg_trace_occ = get_avg_trace_occ(log, key, activities)
        
        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_avg_trace_occ = sorted(avg_trace_occ.items(), key=lambda x: x[1])
        # Build input order
        # most frequent element is minimal
        for i in reversed(range(len(sorted_avg_trace_occ))):
            for j in reversed(range(i)):
                input_order_builder.add_relation(larger=sorted_avg_trace_occ[j][0], smaller=sorted_avg_trace_occ[i][0])
        
        # Build output order
        # least frequent element is minimal
        for i in range(len(sorted_avg_trace_occ)):
            for j in range(i):
                output_order_builder.add_relation(larger=sorted_avg_trace_occ[j][0], smaller=sorted_avg_trace_occ[i][0])

        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

class MaxUnderfedPlacesThroughAbsTraceFreqOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        # A place is more likely to be underfed, if its' output transitions
        # are more likely to occur in a trace, than the place's input transitons.
        activities = log_util.get_event_labels(log, key)
        abs_trace_occ = get_abs_trace_occ(log, key, activities)
        
        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_abs_trace_occ = sorted(abs_trace_occ.items(), key=lambda x: x[1])
        # Build input order
        # most frequent element is minimal
        for i in reversed(range(len(sorted_abs_trace_occ))):
            for j in reversed(range(i)):
                input_order_builder.add_relation(larger=sorted_abs_trace_occ[j][0], smaller=sorted_abs_trace_occ[i][0])
        
        # Build output order
        # least frequent element is minimal
        for i in range(len(sorted_abs_trace_occ)):
            for j in range(i):
                output_order_builder.add_relation(larger=sorted_abs_trace_occ[j][0], smaller=sorted_abs_trace_occ[i][0])

        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

class MaxUnderfedPlacesThroughRelativeTraceFreqOrderStrategy(OrderCalculationStrategy):

    def execute(self, log, key):
        # A place is more likely to be underfed, if its' output transitions
        # are more likely to occur in a trace, than the place's input transitons.
        activities = log_util.get_event_labels(log, key)
        rel_trace_occ = get_rel_trace_occ(log, key, activities)
        
        input_order_builder  = ActivityOrderBuilder(activities)
        output_order_builder = ActivityOrderBuilder(activities)
        sorted_rel_trace_occ = sorted(rel_trace_occ.items(), key=lambda x: x[1])
        # Build input order
        # most frequent element is minimal
        for i in reversed(range(len(sorted_rel_trace_occ))):
            for j in reversed(range(i)):
                input_order_builder.add_relation(larger=sorted_rel_trace_occ[j][0], smaller=sorted_rel_trace_occ[i][0])
        
        # Build output order
        # least frequent element is minimal
        for i in range(len(sorted_rel_trace_occ)):
            for j in range(i):
                output_order_builder.add_relation(larger=sorted_rel_trace_occ[j][0], smaller=sorted_rel_trace_occ[i][0])

        return (input_order_builder.get_ordering(), output_order_builder.get_ordering())

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
