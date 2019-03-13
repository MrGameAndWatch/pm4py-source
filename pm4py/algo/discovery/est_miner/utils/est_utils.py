from enum import Enum

class PlaceFitnessState(Enum):
    FITTING = 1
    OVERFED = 2
    UNDERFED = 3

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
    - The unique start activity
    - The unique end activity
    """
    return None, None, None

def evaluate_place(log, input_trans, output_trans, tau):
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
    return None