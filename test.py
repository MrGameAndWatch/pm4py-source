import os

from pm4py.algo.discovery.est_miner.builder import EstMinerDirector, TestEstMinerBuilder
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness

def execute_script():
    # loads the log
    log = xes_importer.apply("Log-dependencyXOR1.xes")
    est_miner_director = EstMinerDirector()
    test_est_miner_builder = TestEstMinerBuilder()
    est_miner_director.construct(test_est_miner_builder)
    # apply est-miner
    net, im, fm = test_est_miner_builder.est_miner.apply(log)
    # checks if the Petri net is a sound workflow net
    #is_sound_wfnet = check_petri_wfnet_and_soundness(net)
    #print("is_sound_wfnet = ", is_sound_wfnet)

if __name__ == "__main__":
    execute_script()
