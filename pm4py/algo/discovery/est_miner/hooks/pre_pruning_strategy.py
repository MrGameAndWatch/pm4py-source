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

class ImportantPlacesPrePruning(PrePruningStrategy):

    def __init__(self):
        self._relation_support  = None
        self._log               = None
        self._key               = None
        self._threshold         = None
        self._pre_prune_useless_places = PrePruneUselessPlacesStrategy()
    
    def initialize(self, log, key, activites, threshold=0.9):
        self._log = log
        self._key = key
        self._threshold = threshold
        self._relation_support = self._build_relation_support(log, key, activites)
    
    def execute(self, candidate_place):
        return (
            self._pre_prune_useless_places.execute(candidate_place) or
            self._score_place(candidate_place, self._log, self._key, self._threshold)
        )
    
    def _build_relation_support(self, log, key, activites):
        per_trace_support = self._build_per_trace_support(log, key, activites)
        relation_support = dict()
        for a1 in activites:
            for a2 in activites:
                score = 0
                normalization_factor = 0
                for (trace_key, (freq, trace)) in log.items():
                    score += freq * per_trace_support[trace_key, a1, a2]

                    found_a1 = False
                    found_a2 = False
                    for e in trace:
                        if e[key] == a1:
                            found_a1 = True
                        if e[key] == a2:
                            found_a2 = True
                    if (found_a1 and found_a2):
                        normalization_factor += freq
                if (normalization_factor == 0):
                    relation_support[a1, a2] = 0
                else:
                    relation_support[a1, a2] = (score / normalization_factor)
        return relation_support
    
    def _build_per_trace_support(self, log, key, activites):
        per_trace_support = dict()
        for (trace_key, (freq, trace)) in log.items():
            for a1 in activites:
                for a2 in activites:
                    per_trace_support[trace_key, a1, a2] = self._follows(a1, a2, trace, key)
        return per_trace_support

    def _follows(self, a1, a2, trace, key):
        # Returns True, if a2 eventually follows a1 in the trace
        found_a1 = False
        follows  = 0
        for e in trace:
            if found_a1:
                if e[key] == a2:
                    follows = 1
            if e[key] == a1:
                found_a1 = True
        return follows
    
    def _score_place(self, place, log, key, threshold):
        # Place score should give what percentage of pairwise relations between 
        # input and output activities are important (supported by the log).
        #
        # Assume every pair of input and output activities of the place is contained
        # in each trace, then this place gives an important restriction. If only 
        # some are important, then splitting the place might be a good choice, meaning
        # the place itself and its subplaces are not interesting.
        for a in place.input_trans:
            for b in place.output_trans:
                if a != b and self._relation_support[a, b] < threshold:
                    return True
        return False

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
                if self._follows(self._follow_matrix, pre=output_a, fol=input_a, threshold=1.0):
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
            pre_encountered = False
            follows = False
            for e in trace:
                if pre_encountered:
                    if e[key] == fol:
                        follows = True

                if e[key] == pre:
                    pre_encountered = True
            if follows:
                count += freq
        return count
    
    def _num_traces(self, log):
        num_traces = 0
        for (trace_key, (freq, trace)) in log.items():
            num_traces += freq
        return num_traces
