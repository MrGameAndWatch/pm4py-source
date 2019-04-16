import pathlib
import logging
import os

from pm4py.algo.discovery.est_miner.builder import EstMinerDirector, TestEstMinerBuilder, StandardEstMinerBuilder, \
TraceFrequencyOrderEstMinerBuilder
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness
from pm4py.visualization.petrinet.factory import apply, view, save
from experiments.logging.logger import RuntimeStatisticsLogger
import experiments.visualization.charts as charts

data_set_paths = [
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'artificial-xor-test-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'two-trans-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'repair-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'reviewing-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'teleclaims-set')
]

data_set_file_names = [
    'Log-dependencyXOR1.xes',
    'TwoActivities.xes',
    'repairExample.xes',
    'reviewing.xes',
    'teleclaims.xes'
]

result_folder = 'res'
log_folder    = 'out-logs'
charts_folder = 'charts'

def execute_miner(est_miner, parameters, folder, log_file_name):
    # make sure all folders are there
    if not os.path.exists(os.path.join(folder, est_miner.name, result_folder)):
        os.makedirs(os.path.join(folder, est_miner.name, result_folder))
    if not os.path.exists(os.path.join(folder, est_miner.name, log_folder)):
        os.makedirs(os.path.join(folder, est_miner.name, log_folder))
    if not os.path.exists(os.path.join(folder, est_miner.name, charts_folder)):
        os.makedirs(os.path.join(folder, est_miner.name, charts_folder))

    # activate logging
    file_handler = logging.FileHandler(os.path.join(folder, est_miner.name, log_folder, 'res.log'), mode='w')
    logger = logging.getLogger(est_miner.name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    log = xes_importer.apply(os.path.join(folder, log_file_name))
    net, im, fm, stat_logger = est_miner.apply(log, parameters=parameters, logger=logger)
    gviz = apply(net, initial_marking=im, final_marking=fm)
    save(gviz, os.path.join(folder, est_miner.name, result_folder, 'net.png'))
    charts.plot_runtimes(stat_logger, os.path.join(folder, est_miner.name, charts_folder, 'runtimes.pdf'))

def construct_est_miners():
    est_miners = list()
    est_miner_director = EstMinerDirector()
    standard_est_miner_builder = StandardEstMinerBuilder()
    trace_freq_est_miner_builder = TraceFrequencyOrderEstMinerBuilder()
    est_miner_director.construct(trace_freq_est_miner_builder)
    est_miner_director.construct(standard_est_miner_builder)
    est_miners.append(standard_est_miner_builder.est_miner)
    est_miners.append(trace_freq_est_miner_builder.est_miner)
    return est_miners

def execute_experiments():
    est_miners = construct_est_miners()
    parameters = dict()
    parameters['key'] = 'concept:name'
    parameters['tau'] = 1
    for i in range(0, len(data_set_paths)):
        for est_miner in est_miners:
            execute_miner(est_miner, parameters, data_set_paths[i], data_set_file_names[i])

if __name__ == "__main__":
    execute_experiments()
