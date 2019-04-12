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
