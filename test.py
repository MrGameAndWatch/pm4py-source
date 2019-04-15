import pathlib
import logging
import os

from pm4py.algo.discovery.est_miner.builder import EstMinerDirector, TestEstMinerBuilder, StandardEstMinerBuilder
from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness
from pm4py.visualization.petrinet.factory import apply, view, save
from experiments.logging.logger import RuntimeStatisticsLogger
import experiments.visualization.charts as charts

data_set_paths = [
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'artificial-xor-test-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'two-trans-set')
]

data_set_file_names = [
    'Log-dependencyXOR1.xes',
    'TwoActivities.xes'
]

result_folder = 'res'
log_folder    = 'out-logs'

def execute_script():
    for i in range(0, len(data_set_paths)):

        # activate logging
        file_handler = logging.FileHandler(os.path.join(data_set_paths[i], log_folder, 'res.log'), mode='w')
        logger = logging.getLogger('est_miner_logger')
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        # loads the log
        log = xes_importer.apply(os.path.join(data_set_paths[i], data_set_file_names[i]))
        est_miner_director = EstMinerDirector()
        standard_est_miner_builder = StandardEstMinerBuilder()
        est_miner_director.construct(standard_est_miner_builder)
        # apply est-miner
        parameters = dict()
        parameters['key'] = 'concept:name'
        parameters['tau'] = 1
        net, im, fm, stat_logger = standard_est_miner_builder.est_miner.apply(log, parameters=parameters, logger=logger)
        gviz = apply(net, initial_marking=im, final_marking=fm)
        save(gviz, pathlib.Path(data_set_paths[i], result_folder, 'net.png'))
        charts.plot_runtimes(stat_logger, pathlib.Path(data_set_paths[i], result_folder))
        #charts.plot_pruned_places(stat_logger, path)


if __name__ == "__main__":
    execute_script()
