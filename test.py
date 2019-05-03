import pathlib
import logging
import os

from pm4py.algo.discovery.est_miner.builder import EstMinerDirector, TestEstMinerBuilder, StandardEstMinerBuilder, \
MaxCutoffsAbsFreqEstMinerBuilder, MaxCutoffsRelTraceFreqEstMinerBuilder, RestrictBlueEdgesAndMaxCutoffsAbsTraceFreqEstMinerBuilder, \
MaxCutoffsRelTraceFreqHeuristicPruningEstMinerBuilder, AlphaMinerRefinementSearchEstMinerBuilder, \
PlaceInterestPrePruningRestrictRedEdgesEstMinerBuilder

from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness
from pm4py.visualization.petrinet.factory import apply, view, save
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.replay_fitness import factory as fitness_factory
from pm4py.evaluation.simplicity import factory as simplicity_factory
from experiments.logging.logger import RuntimeStatisticsLogger
import experiments.visualization.charts as charts

data_set_paths = [
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'dominiks-log'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'artificial-xor-test-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'two-trans-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'repair-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'reviewing-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'teleclaims-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'sepsis-mod-set'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'road-traffic-fine-set')
]

data_set_file_names = [
#    'APM_Assignment_1.xes',
    'Log-dependencyXOR1.xes',
    'TwoActivities.xes',
    'repairExample.xes',
    'reviewing.xes',
    'teleclaims.xes',
    'sepsis.xes',
    'road-traffic-fines.xes'
]

result_folder = 'res'
log_folder    = 'out-logs'
charts_folder = 'charts'

def evaluate_net(log, net, initial_marking, final_marking, data_set_path, est_miner_name):
    fitness = fitness_factory.apply(log, net, initial_marking, final_marking)
    precision = precision_factory.apply(log, net, initial_marking, final_marking)
    generalization = generalization_factory.apply(log, net, initial_marking, final_marking)
    simplicity = simplicity_factory.apply(net)
    charts.plot_evaluation(fitness, precision, generalization, simplicity, os.path.join(data_set_path, est_miner_name, charts_folder, 'metrics.pdf'))

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
    evaluate_net(log, net, im, fm, folder, est_miner.name)
    gviz = apply(net, initial_marking=im, final_marking=fm)
    save(gviz, os.path.join(folder, est_miner.name, result_folder, 'net.png'))
    return stat_logger

def construct_est_miners():
    est_miners = list()
    est_miner_director = EstMinerDirector()
    standard_est_miner_builder = StandardEstMinerBuilder()
    max_cutoffs_abs_trace_freq_est_miner_builder = MaxCutoffsAbsFreqEstMinerBuilder()
    max_cutoffs_rel_trace_freq_est_miner_builder = MaxCutoffsRelTraceFreqEstMinerBuilder()
    max_cutoffs_abs_trace_freq_restricted_blue_edges_est_miner_builder = RestrictBlueEdgesAndMaxCutoffsAbsTraceFreqEstMinerBuilder()
    max_cutoffs_rel_trace_freq_heuristic_pruning_est_miner_builder = MaxCutoffsRelTraceFreqHeuristicPruningEstMinerBuilder()
    alpha_miner_refinment_search_est_miner_builder = AlphaMinerRefinementSearchEstMinerBuilder()
    interest_places_pre_pruning_est_miner_builder = PlaceInterestPrePruningRestrictRedEdgesEstMinerBuilder()
    est_miner_director.construct(standard_est_miner_builder)
    est_miner_director.construct(max_cutoffs_abs_trace_freq_est_miner_builder)
    est_miner_director.construct(max_cutoffs_rel_trace_freq_est_miner_builder)
    est_miner_director.construct(max_cutoffs_abs_trace_freq_restricted_blue_edges_est_miner_builder)
    est_miner_director.construct(max_cutoffs_rel_trace_freq_heuristic_pruning_est_miner_builder)
    est_miner_director.construct(alpha_miner_refinment_search_est_miner_builder)
    est_miner_director.construct(interest_places_pre_pruning_est_miner_builder)
    est_miners.append(standard_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_abs_trace_freq_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_rel_trace_freq_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_abs_trace_freq_restricted_blue_edges_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_rel_trace_freq_heuristic_pruning_est_miner_builder.est_miner)
    #est_miners.append(alpha_miner_refinment_search_est_miner_builder.est_miner)
    est_miners.append(interest_places_pre_pruning_est_miner_builder.est_miner)
    return est_miners

def create_statistics(stat_loggers, data_set_path):
    for stat_logger in stat_loggers:
        charts.plot_runtimes(stat_logger, os.path.join(data_set_path, stat_logger.est_miner_name, charts_folder, 'runtimes.pdf'))
        charts.plot_pruned_places(stat_logger, os.path.join(data_set_path, stat_logger.est_miner_name, charts_folder, 'cutoffs.pdf'))

def execute_experiments():
    est_miners = construct_est_miners()
    parameters = dict()
    parameters['key'] = 'concept:name'
    parameters['tau'] = 1
    parameters['alpha'] = 0.5
    for i in range(0, len(data_set_paths)):
        stat_loggers = list()
        for est_miner in est_miners:
            stat_logger = execute_miner(est_miner, parameters, data_set_paths[i], data_set_file_names[i])
            stat_loggers.append(stat_logger)
        create_statistics(stat_loggers, data_set_paths[i])

if __name__ == "__main__":
    execute_experiments()
