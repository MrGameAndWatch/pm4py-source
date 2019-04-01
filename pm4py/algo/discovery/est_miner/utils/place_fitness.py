from enum import Enum

from pm4py.algo.discovery.est_miner.utils.place import Place

class State(Enum):
    FITTING = 1
    OVERFED = 2
    UNDERFED = 3
    UNFITTING = 4

class PlaceFitnessEvaluator:

    @classmethod
    def evaluate_place_fitness(cls, log, place, tau):
        overfed_traces = 0
        underfed_traces = 0
        fitting_traces = 0
        involved_traces = 0

        for trace in log:
            involved, states = cls.trace_fitness(trace, place)
            if State.UNDERFED in states: underfed_traces += 1
            if State.OVERFED  in states: overfed_traces  += 1
            if State.FITTING  in states: fitting_traces  += 1
            if involved:                 involved_traces += 1
        
        return cls.place_states(
            overfed_traces, 
            underfed_traces, 
            fitting_traces, 
            involved_traces, 
            tau
        )

    @classmethod
    def trace_fitness(cls, trace, place):
        tokens = 0
        involved = False
        states = set()
        for event in trace:
            if event in place.input_trans or event in place.output_trans:
                involved = True
            if event in place.input_trans:
                tokens += 1
            elif event in place.output_trans:
                tokens -= 1
            if tokens < 0:
                states.add(State.UNDERFED)

        if tokens > 0:
            states.add(State.OVERFED)
        elif tokens == 0 and State.UNDERFED not in states:
            states.add(State.FITTING)

        return involved, states
    
    @classmethod
    def place_states(cls, overfed_traces, underfed_traces, involved_traces, fitting_traces, tau):
        states = set()
        if cls.is_overfed(overfed_traces, involved_traces, tau):   states.add(State.OVERFED)
        if cls.is_underfed(underfed_traces, involved_traces, tau): states.add(State.UNDERFED)
        if cls.is_fitting(fitting_traces, involved_traces, tau):   states.add(State.FITTING)
        else:                                                      states.add(State.UNFITTING)
        return states
    
    @classmethod
    def is_overfed(cls, overfed_traces, involved_traces, tau):
        return (overfed_traces / involved_traces) > (1 - tau)
    
    @classmethod
    def is_underfed(cls, underfed_traces, involved_traces, tau):
        return (underfed_traces / involved_traces) > (1 - tau)
    
    @classmethod
    def is_fitting(cls, fitting_traces, involved_traces, tau):
        return (fitting_traces / involved_traces) >= tau
