import os
import unittest

from pm4py.algo.conformance.alignments import algorithm as align_alg
from pm4py.algo.discovery.alpha import algorithm as alpha_alg
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects import petri
from pm4py.objects.log.importer.xes import importer as xes_importer
from tests.constants import INPUT_DATA_DIR


class AlignmentTest(unittest.TestCase):
    def test_alignment_alpha(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, fmarking = alpha_alg.apply(log)
        final_marking = petri.petrinet.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in log:
            cf_result = \
            align_alg.apply(trace, net, marking, final_marking, variant=align_alg.VERSION_DIJKSTRA_NO_HEURISTICS)[
                'alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")

    def test_alignment_pnml(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        for trace in log:
            cf_result = \
            align_alg.apply(trace, net, marking, final_marking, variant=align_alg.VERSION_DIJKSTRA_NO_HEURISTICS)[
                'alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")


if __name__ == "__main__":
    unittest.main()
