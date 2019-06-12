import pm4py.objects.log.util.log as log_util
import pm4py.algo.discovery.est_miner.utils.constants as constants
import pm4py.algo.discovery.est_miner.utils.place_fitness as place_fitness

def insert_unique_start_and_end_activity(log):
    """
    Insert a unique start and end activity for each trace in the log.

    Parameters:
    ---------
    log: :class:`pm4py.log.log.EventLog`
            The event log of traces
    
    Returns:
    ---------
    - The log with the transformed traces
    """
    return log_util.add_artificial_start_and_end(
        log, 
        start=constants.START_ACTIVITY, 
        end=constants.END_ACTIVITY
    )

def optimize_for_replay(log, key):
    events = log_util.get_event_labels(log, key)
    events_bitmasks    = dict()
    bitmasks_to_events = dict()
    activities         = list()
    start_activity     = 0
    end_activity       = 0
    for i in range(len(events)):
        bitmask = ''
        for j in range(len(events)):
            if (i == j):
                bitmask += '1'
            else:
                bitmask += '0'
        encoded_event = int(bitmask, 2)
        events_bitmasks[events[i]] = encoded_event # Encoded as integer
        bitmasks_to_events[encoded_event] = events[i]
        if (events[i] == constants.START_ACTIVITY):
            start_activity = encoded_event
        if (events[i] == constants.END_ACTIVITY):
            end_activity = encoded_event
        activities.append(encoded_event)
    print(events)
    print(events_bitmasks)
    print(activities)
        
    optimized_log = dict()
    for trace in log:
        trace_bitstring = trace_bitmap(trace, events_bitmasks, key)
        trace_str = trace_string(trace, key)
        if trace_str not in optimized_log:
            optimized_log[trace_str] = [1, trace_bitstring]
        else:
            optimized_log[trace_str][0] += 1
    return optimized_log, activities, start_activity, end_activity, bitmasks_to_events

def most_common_traces(log, num_most_common=1):
    most_common_traces = dict()
    for (trace_key, (freq, trace_bit_string)) in log.items():
        if len(most_common_traces) < num_most_common:
            most_common_traces[trace_key] = freq
        else:
            least_freq_of_most_freq_traces = min(most_common_traces, key=most_common_traces.get)
            if most_common_traces[least_freq_of_most_freq_traces] < freq:
                most_common_traces.pop(least_freq_of_most_freq_traces)
                most_common_traces[trace_key] = freq
    res = list()
    for trace_key in most_common_traces:
        res.append(log[trace_key][1])
    return res

# def optimize_for_replay(log, key):
#     """
#     Output a log as dictionary {trace: freq} to optimize the replay of the log.

#     Parameters:
#     log: :class:`pm4py.log.log.EventLog`
#             The event log of traces
    
#     Returns:
#     - Newly formated log
#     """
#     events = log_util.get_event_labels(log, key)
#     events_to_int = dict()
#     ints_to_events = dict()
#     activities = list()
#     start_activity = 0
#     end_activity = 0
#     for i in range(0, len(events)):
#         activities.append(i)
#         events_to_int[events[i]] = i # converted events to integers
#         ints_to_events[i] = events[i]
#         if (events[i] == constants.START_ACTIVITY):
#             start_activity = i
#         if (events[i] == constants.END_ACTIVITY):
#             end_activity = i

#     optimized_log = dict()
#     for trace in log:
#         trace_bitstring = trace_bitmap(trace, events_to_int, key)
#         trace_str = trace_string(trace, key)
#         if trace_str not in optimized_log:
#             optimized_log[trace_str] = [1, trace_bitstring]
#         else:
#             optimized_log[trace_str][0] += 1
#     return optimized_log, activities, start_activity, end_activity, ints_to_events

def trace_bitmap(trace, events_to_int, key):
    res = list()
    for e in trace:
        res.append(events_to_int[e[key]])
    return res

def trace_string(trace, key):
    events = list()
    for e in trace:
        events.append(e[key])
    return str(events)

def construct_net(log, resulting_places):
    """
    Construct the petri net, given the found set of places.

    Parameters:
    ---------
    log :class:`pm4py.log.log.EventLog`
            Event log to use for replay
    resulting_places: Set of places found by the algorithm

    Returns:
    ---------
    - The net
    - The initial marking
    - The final marking
    """
    return None, None, None
