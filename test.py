import os
import logging

from pm4py.algo.discovery.est_miner.builder import EstMinerDirector, TestEstMinerBuilder, StandardEstMinerBuilder
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness
from pm4py.visualization.petrinet.factory import apply, view, save
from experiments.logging.logger import RuntimeStatisticsLogger
import experiments.visualization.charts as charts

def execute_script():
    path = ''
    # activate logging
    file_handler = logging.FileHandler('test.log', mode='w')
    logger = logging.getLogger('est_miner_logger')
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    # loads the log
    log = xes_importer.apply("Log-dependencyXOR1.xes")
    est_miner_director = EstMinerDirector()
    standard_est_miner_builder = StandardEstMinerBuilder()
    est_miner_director.construct(standard_est_miner_builder)
    # apply est-miner
    parameters = dict()
    parameters['key'] = 'concept:name'
    parameters['tau'] = 1
    net, im, fm, stat_logger = standard_est_miner_builder.est_miner.apply(log, parameters=parameters, logger=logger)
    gviz = apply(net, initial_marking=im, final_marking=fm)
    view(gviz)
    #charts.plot_runtimes(stat_logger, path)
    #charts.plot_pruned_places(stat_logger, path)


if __name__ == "__main__":
    execute_script()
