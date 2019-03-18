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

def evaluate_place(log, place, tau):
    """
    Evaluate if a given place is underfed or overfed based on replaying
    the log.

    Parameters:
    ---------
    log :class:`pm4py.log.log.EventLog`
            Event log to use for replay
    input_trans: Set of input transitions of the place
    output_trans: Set of output transitions of the place
    tau: Noise filtering parameter of the algorithm

    Returns:
    ---------
    A collection of the place's fitness states.
    """
    return place_fitness.PlaceFitnessEvaluator.evaluate_place_fitness(log, place, tau)

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
