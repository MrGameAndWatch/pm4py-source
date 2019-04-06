import os

from pm4py.algo.discovery.est_miner.builder import EstMinerDirector, TestEstMinerBuilder, StandardEstMinerBuilder
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness

def execute_script():
    # loads the log
    log = xes_importer.apply("Log-dependencyXOR1.xes")
    est_miner_director = EstMinerDirector()
    standard_est_miner_builder = StandardEstMinerBuilder()
    est_miner_director.construct(standard_est_miner_builder)
    # apply est-miner
    parameters = dict()
    parameters['key'] = 'concept:name'
    parameters['tau'] = 1
    resulting_places, im, fm = standard_est_miner_builder.est_miner.apply(log, parameters=parameters)

    for place in resulting_places:
        print('Input: ')
        print(place.input_trans)
        print('| Output: ')
        print(place.output_trans)

if __name__ == "__main__":
    execute_script()
