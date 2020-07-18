from pm4py.objects.log import log as event_log
from pm4py.util import xes_constants as xes_utils

def add_unique_start_and_end_activity(log, start='[start>', end='[end]', activity_key=xes_utils.DEFAULT_NAME_KEY):
    for trace in log:
        trace.insert(0, event_log.Event({activity_key: start}))
        trace.append(event_log.Event({activity_key: end}))
    return log
