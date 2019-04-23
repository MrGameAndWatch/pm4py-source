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
    """
    Output a log as dictionary {trace: freq} to optimize the replay of the log.

    Parameters:
    log: :class:`pm4py.log.log.EventLog`
            The event log of traces
    
    Returns:
    - Newly formated log
    """
    optimized_log = dict()
    for trace in log:
        trace_str = trace_string(trace, key)
        if trace_str not in optimized_log:
            optimized_log[trace_str] = [1, trace]
        else:
            optimized_log[trace_str][0] += 1
    return optimized_log

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
