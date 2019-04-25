import abc
from collections import defaultdict

import pm4py.algo.discovery.est_miner.utils.constants as const

class PrePruningStrategy(abc.ABC):

    @abc.abstractmethod
    def initialize(self, log, key, activites):
        """
        Initialize potential heuristics.
        """
        pass

    @abc.abstractmethod
    def execute(self, candidate_place):
        """
        Evaluate if the given candidate place is already
        pruned.
        """
        pass

class NoPrePruningStrategy(PrePruningStrategy):

    def initialize(self, log, key, activites):
        pass

    def execute(self, candidate_place):
        print('Executed Pre Pruning')
        return False

class PrePruneUselessPlacesStrategy(PrePruningStrategy):

    def initialize(self, log, key, activites):
        pass

    def execute(self, candidate_place):
        return (
            const.END_ACTIVITY in candidate_place.input_trans 
            or const.START_ACTIVITY in candidate_place.output_trans 
        )

class HeuristicPrePrune(PrePruningStrategy):

    def __init__(self):
        self._follow_matrix = None
        self._pre_prune_useless_places = PrePruneUselessPlacesStrategy()

    def initialize(self, log, key, activites):
        self._follow_matrix = self._build_follow_matrix(log, key, activites)

    def execute(self, candidate_place):
        prune = False
        for input_a in candidate_place.input_trans:
            for output_a in candidate_place.output_trans:
                if self._follows(self._follow_matrix, pre=output_a, fol=input_a, threshold=0.95):
                    prune = True
        return (prune or self._pre_prune_useless_places.execute(candidate_place))

    def _build_follow_matrix(self, log, key, activites):
        num_traces = self._num_traces(log)
        follow_matrix = defaultdict(dict)
        for a1 in activites:
            for a2 in activites:
                a1_follows_a2 = self._num_follows(log, key, a1, a2) / num_traces
                a2_follows_a1 = self._num_follows(log, key, a2, a1) / num_traces
                follow_matrix[a1][a2] = a2_follows_a1
                follow_matrix[a2][a1] = a1_follows_a2
        return follow_matrix
    
    def _follows(self, follow_matrix, pre=None, fol=None, threshold=0):
        assert(pre in follow_matrix and fol in follow_matrix)
        return follow_matrix[pre][fol] > threshold
    
    def _num_follows(self, log, key, pre, fol):
        count = 0
        for (trace_key, (freq, trace)) in log.items():
            for e in trace:
                last_pos = 0
                pos = 0
                if e[key] == fol:
                    last_pos = pos
                    while pos >= 0: # backtrack
                        if trace[pos][key] == pre:
                            count += freq
                        pos -= 1
                    pos = last_pos
                pos += 1
        return count
    
    def _num_traces(self, log):
        num_traces = 0
        for (trace_key, (freq, trace)) in log.items():
            num_traces += freq
        return num_traces
