from pm4py.objects.log import log as event_log
from pm4py.objects.log.util import log as log_util
from pm4py.util import xes_constants as xes_utils

def add_unique_start_and_end_activity(log, start='[start>', end='[end]', activity_key=xes_utils.DEFAULT_NAME_KEY):
    for trace in log:
        trace.insert(0, event_log.Event({activity_key: start}))
        trace.append(event_log.Event({activity_key: end}))
    return log

"""
Transforms each event in each trace into a bitmask vector and returns the resulting log.

Assume that we have the events {a, b, c} in the log. Then the following mapping
is created: a => 001, b => 010, c => 100.
This is used to perform token based replay faster:
Assume we have the trace <a, a, b, c> and we need to replay the trace on a given
Petri-net with the places {a, b, c}. Then without using bitmasks, we need
to perform at least one string comparison for each activity in the trace.
In contrast, if we have bitmasked the events, then we have the trace
<001, 001, 010, 100> and only need to perform a bitwise & for each previous
required string comparison. This is a lot faster to do.
"""
def transform_to_bitmasked_log(log, activity_key=xes_utils.DEFAULT_NAME_KEY):
    def build_event_to_bitmask_map():
        events = log_util.get_event_labels(log, activity_key)
        mapping = dict()
        for i in range(len(events)):
            bitmask = 1 << i
            mapping[events.__getitem__(i)] = bitmask
        return mapping

    mapping = build_event_to_bitmask_map()
    bitmasked_log = event_log.EventLog()
    for trace in log:
        bitmasked_trace = event_log.Trace()
        for event in trace:
            bitmasked_trace.append(mapping.get(event[activity_key]))
        bitmasked_log.append(bitmasked_trace)
    return bitmasked_log
