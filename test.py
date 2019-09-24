import pathlib
import logging
import os
import csv
import time

from pm4py.algo.discovery.est_miner.builder \
import EstMinerDirector, TestEstMinerBuilder, StandardEstMinerBuilder, \
MaxCutoffsAbsFreqEstMinerBuilder, MaxCutoffsRelTraceFreqEstMinerBuilder, \
RestrictBlueEdgesAndMaxCutoffsAbsTraceFreqEstMinerBuilder, \
MaxUnderfedAvgTraceOccEstMinerBuilder, MaxUnderfedAvgFirstOccIndexEstMinerBuilder, \
AlternativeInterestingPlacesEstMinerBuilder, RestrictNumInAndOutTransitionsEstMinerBuilder, \
ImportantTracesEstMinerBuilder, PrePruningAndReduceComplexityPostProcessingEstMinerBuilder, \
IntersetingPlacesAntiSelfLoopsEstMinerBuilder, ColoredDfgEstMinerBuilder, \
MaxCutoffsAverageFirstOccurrenceIndexEstMinerBuilder, MaxCutoffsAverageTraceOccurrenceEstMinerBuilder, \
MaxCutoffsAbsoluteTraceFrequencyEstMinerBuilder, MaxCutoffsAbsoluteActivityFrequencyEstMinerBuilder, \
InterestingPlacesEstMinerBuilder

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
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.statistics.traces.log import case_statistics


data_set_paths = [
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'dominiks-log'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'artificial-xor-test-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'two-trans-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'repair-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'reviewing-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'teleclaims-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'sepsis-mod-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'road-traffic-fine-set'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'sepsis-pre-processed'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'basILP40'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'LogXOR-AND'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'LogXOR2'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'alpha++-fail1'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'one-choice-log'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'sepsis-ten-occ')
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'BPIChallenge'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'teleclaims-mod'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'rtfm-mod'),
    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'sepsis-filtered'),
#    os.path.join(pathlib.Path.home(), 'Documents', 'Studium', 'Masterarbeit', 'experimental-eval', 'hospital-billing'),
]

data_set_file_names = [
#    'APM_Assignment_1.xes',
#    'Log-dependencyXOR1.xes',
#    'TwoActivities.xes',
#    'repairExample.xes',
#    'reviewing.xes',
#    'teleclaims.xes',
#    'sepsis.xes',
#    'road-traffic-fines.xes',
#    'Sepsis-doubletracesout.xes',
#    'test40.xes',
#    'Log-xor-and.xes',
#    'Log-dependencyXOR2.xes',
#    'alpha++fail1.xes',
#    'one-choice-log.xes',
#    'sepsis-ten-occ.xes',
#    'bpi-challenge-2017-reduced.xes',
#    'teleclaims-mod.xes',
#    'rtfm-mod.xes',
    'sepsis-filtered.xes',
#    'hospital-billing.xes',
]

tau_folder    = 'tau={tau}'
result_folder = 'res'
log_folder    = 'out-logs'
charts_folder = 'charts'
statistics_file_name = 'statistics.csv'
conformance_stats_file = 'conformance.csv'

NUM_RUNS = 1

def evaluate_net(log, net, initial_marking, final_marking, path):
    fitness = fitness_factory.apply(log, net, initial_marking, final_marking)
    precision = precision_factory.apply(log, net, initial_marking, final_marking)
    generalization = generalization_factory.apply(log, net, initial_marking, final_marking)
    simplicity = simplicity_factory.apply(net)
    avg_trans_in_degree, avg_trans_out_degree, avg_place_in_degree, avg_place_out_degree = simplicity_factory.apply(net, variant="avg_degree")
    num_edges = simplicity_factory.apply(net, variant="num_edges")
    column_names = [
        'fitness', 
        'precision', 
        'generalization', 
        'simplicity', 
        'avg-trans-in-degree', 
        'avg-trans-out-degree',
        'avg-place-in-degree',
        'avg-place-out-degree',
        'num-edges'
    ]
    row = []
    row.append(fitness)
    row.append(precision)
    row.append(generalization)
    row.append(simplicity)
    row.append(avg_trans_in_degree)
    row.append(avg_trans_out_degree)
    row.append(avg_place_in_degree)
    row.append(avg_place_out_degree)
    row.append(num_edges)
    
    with open(os.path.join(path, conformance_stats_file), 'w') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerow(row)
    file.close()
    #charts.plot_evaluation(fitness, precision, generalization, simplicity, os.path.join(path, est_miner_name, charts_folder, 'metrics.pdf'))

def execute_miner(est_miner, parameters, folder, log_file_name):
    tau_sub_folder = tau_folder.format(tau=parameters['tau'])
    # make sure all folders are there
    if not os.path.exists(os.path.join(folder, tau_sub_folder, charts_folder)):
        os.makedirs(os.path.join(folder, tau_sub_folder, charts_folder))
    if not os.path.exists(os.path.join(folder, tau_sub_folder)):
        os.makedirs(os.path.join(folder, tau_sub_folder))
    if not os.path.exists(os.path.join(folder, tau_sub_folder, est_miner.name, result_folder)):
        os.makedirs(os.path.join(folder, tau_sub_folder, est_miner.name, result_folder))
    if not os.path.exists(os.path.join(folder, tau_sub_folder, est_miner.name, log_folder)):
        os.makedirs(os.path.join(folder, tau_sub_folder, est_miner.name, log_folder))
    if not os.path.exists(os.path.join(folder, tau_sub_folder, est_miner.name, charts_folder)):
        os.makedirs(os.path.join(folder, tau_sub_folder, est_miner.name, charts_folder))

    # activate logging
    file_handler = logging.FileHandler(os.path.join(folder, tau_sub_folder, est_miner.name, log_folder, 'res.log'), mode='w')
    logger = logging.getLogger(est_miner.name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    log = xes_importer.apply(os.path.join(folder, log_file_name))
    net, im, fm, stat_logger = est_miner.apply(log, parameters=parameters, logger=logger)
    evaluate_net(log, net, im, fm, os.path.join(folder, tau_sub_folder, est_miner.name, result_folder))
    gviz = apply(net, initial_marking=im, final_marking=fm)
    save(gviz, os.path.join(folder, tau_sub_folder, est_miner.name, result_folder, 'net.png'))
    #create_statistic(stat_logger, os.path.join(folder, tau_sub_folder, est_miner.name, charts_folder))
    #stat_logger.to_file(os.path.join(folder, tau_sub_folder, est_miner.name, 'stat_logger.StatLogger'))
    return stat_logger

def create_statistic(stat_logger, path):
    # write to file
    # charts
    charts.plot_runtimes(stat_logger, os.path.join(path, 'runtimes.pdf'))
    charts.plot_runtimes(stat_logger, os.path.join(path, 'runtimes.png'))
    charts.plot_pruned_places(stat_logger, os.path.join(path, 'cutoffs.pdf'))
    charts.plot_pruned_places(stat_logger, os.path.join(path, 'cutoffs.png'))

def construct_est_miners():
    est_miners = list()
    est_miner_director = EstMinerDirector()
    standard_est_miner_builder = StandardEstMinerBuilder()

    max_cutoffs_abs_trace_freq_est_miner_builder = MaxCutoffsAbsFreqEstMinerBuilder()
    max_cutoffs_rel_trace_freq_est_miner_builder = MaxCutoffsRelTraceFreqEstMinerBuilder()
    max_cutoffs_abs_trace_freq_restricted_blue_edges_est_miner_builder = RestrictBlueEdgesAndMaxCutoffsAbsTraceFreqEstMinerBuilder()
    #alpha_miner_refinment_search_est_miner_builder = AlphaMinerRefinementSearchEstMinerBuilder()
    max_underfed_avg_trace_occ_est_miner_builder = MaxUnderfedAvgTraceOccEstMinerBuilder()
    max_underfed_avg_first_occ_index_est_miner_builder = MaxUnderfedAvgFirstOccIndexEstMinerBuilder()
    alternative_interesting_places_est_miner_builder = AlternativeInterestingPlacesEstMinerBuilder()
    restrict_num_in_out_trans_est_miner_builder = RestrictNumInAndOutTransitionsEstMinerBuilder()
    important_traces_est_miner_builder = ImportantTracesEstMinerBuilder()
    reduce_complexity_est_miner_builder = PrePruningAndReduceComplexityPostProcessingEstMinerBuilder()
    anti_self_loops_interesting_places_est_miner_builder = IntersetingPlacesAntiSelfLoopsEstMinerBuilder()
    colored_dfg_est_miner_builder = ColoredDfgEstMinerBuilder()
    avg_first_occurence_index_est_miner_builder = MaxCutoffsAverageFirstOccurrenceIndexEstMinerBuilder()
    avg_trace_occ_est_miner_builder = MaxCutoffsAverageTraceOccurrenceEstMinerBuilder()
    abs_trace_freq_est_miner_builder = MaxCutoffsAbsoluteTraceFrequencyEstMinerBuilder()
    abs_activity_freq_est_miner_builder = MaxCutoffsAbsoluteActivityFrequencyEstMinerBuilder()
    interesting_places_est_miner_builder = InterestingPlacesEstMinerBuilder()

    est_miner_director.construct(standard_est_miner_builder)
    est_miner_director.construct(interesting_places_est_miner_builder)
    est_miner_director.construct(max_cutoffs_abs_trace_freq_est_miner_builder)
    est_miner_director.construct(max_cutoffs_rel_trace_freq_est_miner_builder)
    est_miner_director.construct(max_cutoffs_abs_trace_freq_restricted_blue_edges_est_miner_builder)
    #est_miner_director.construct(alpha_miner_refinment_search_est_miner_builder)
    est_miner_director.construct(max_underfed_avg_trace_occ_est_miner_builder)
    est_miner_director.construct(max_underfed_avg_first_occ_index_est_miner_builder)
    est_miner_director.construct(alternative_interesting_places_est_miner_builder)
    est_miner_director.construct(restrict_num_in_out_trans_est_miner_builder)
    est_miner_director.construct(important_traces_est_miner_builder)
    est_miner_director.construct(reduce_complexity_est_miner_builder)
    est_miner_director.construct(anti_self_loops_interesting_places_est_miner_builder)
    est_miner_director.construct(colored_dfg_est_miner_builder)
    est_miner_director.construct(avg_first_occurence_index_est_miner_builder)
    est_miner_director.construct(avg_trace_occ_est_miner_builder)
    est_miner_director.construct(abs_trace_freq_est_miner_builder)
    est_miner_director.construct(abs_activity_freq_est_miner_builder)

    #est_miners.append(standard_est_miner_builder.est_miner)
    est_miners.append(interesting_places_est_miner_builder.est_miner)
    #est_miners.append(avg_first_occurence_index_est_miner_builder.est_miner)
    #est_miners.append(avg_trace_occ_est_miner_builder.est_miner)
    #est_miners.append(abs_trace_freq_est_miner_builder.est_miner)
    #est_miners.append(abs_activity_freq_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_abs_trace_freq_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_rel_trace_freq_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_abs_trace_freq_restricted_blue_edges_est_miner_builder.est_miner)
    #est_miners.append(max_cutoffs_rel_trace_freq_heuristic_pruning_est_miner_builder.est_miner)
    #est_miners.append(alpha_miner_refinment_search_est_miner_builder.est_miner)
    #est_miners.append(max_underfed_avg_trace_occ_est_miner_builder.est_miner)
    #est_miners.append(max_underfed_avg_first_occ_index_est_miner_builder.est_miner)
    #est_miners.append(interest_places_pre_pruning_est_miner_builder.est_miner)
    #est_miners.append(alternative_interesting_places_est_miner_builder.est_miner)
    #est_miners.append(restrict_num_in_out_trans_est_miner_builder.est_miner)
    #est_miners.append(important_traces_est_miner_builder.est_miner)
    #est_miners.append(reduce_complexity_est_miner_builder.est_miner)
    #est_miners.append(anti_self_loops_interesting_places_est_miner_builder.est_miner)
    #est_miners.append(colored_dfg_est_miner_builder.est_miner)

    return est_miners

def create_dataset_charts(stat_loggers, path):
    # charts
    charts.plot_runtime_comparison(stat_loggers, os.path.join(path, charts_folder, 'runtime_comp.pdf'))
    charts.plot_runtime_comparison(stat_loggers, os.path.join(path, charts_folder, 'runtime_comp.png'))

def save_stats_to_file(stat_logger, path):
    if not os.path.exists(path):
        os.makedirs(path)
    column_names = [
        'MinerName', 
        'AlgoRunTime(s)', 
        'SearchRunTime(s)',
        'PostProcessingRunTime(s)',
        'PrunedPlaces'
    ]


    row = []
    row.append(stat_logger.est_miner_name)
    row.append(stat_logger.algo_runtime(unit='s'))
    row.append(stat_logger.search_runtime(unit='s'))
    row.append(stat_logger.post_processing_runtime(unit='s'))
    row.append(stat_logger.total_pruned_places())
    
    if not os.path.isfile(os.path.join(path, statistics_file_name)):
        with open(os.path.join(path, statistics_file_name), 'w') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
        file.close()

    with open(os.path.join(path, 'statistics.csv'), 'a') as file:
        writer = csv.writer(file)
        writer.writerow(row)
    file.close()

def execute_experiments():
    taus = [1.0]#, 0.9, 0.8, 0.7, 0.6, 0.5]
    for tau in taus:
        est_miners = construct_est_miners()
        parameters = dict()
        parameters['key'] = 'concept:name'
        parameters['tau'] = tau

        for i in range(0, len(data_set_paths)):
            stat_loggers = dict()
            tau_sub_folder = tau_folder.format(tau=parameters['tau'])
            for est_miner in est_miners:
                stat_loggers[est_miner.name] = list()
                for j in range(NUM_RUNS):
                    stat_logger = execute_miner(est_miner, parameters, data_set_paths[i], data_set_file_names[i])
                    save_stats_to_file(stat_logger, os.path.join(data_set_paths[i], tau_sub_folder, 'stats'))
                    #stat_loggers[est_miner.name].append(stat_logger)
            #create_dataset_charts(stat_loggers, os.path.join(data_set_paths[i], tau_sub_folder))
            #save_stats_to_file(stat_loggers, os.path.join(data_set_paths[i], tau_sub_folder, 'stats'))
            if not os.path.exists(os.path.join(data_set_paths[i], tau_sub_folder, 'INDUCTIVE', result_folder)):
                os.makedirs(os.path.join(data_set_paths[i], tau_sub_folder, 'INDUCTIVE', result_folder))
            if not os.path.exists(os.path.join(data_set_paths[i], tau_sub_folder, 'ALPHA', result_folder)):
                os.makedirs(os.path.join(data_set_paths[i], tau_sub_folder, 'ALPHA', result_folder))
            log = xes_importer.import_log(os.path.join(data_set_paths[i], data_set_file_names[i]))
            #log = variants_filter.apply_auto_filter(log, parameters={'decreasingFactor': 0.9})
            start_time = time.time()
            net, initial_marking, final_marking = inductive_miner.apply(log, variant='imdfa')
            end_time = time.time()
            print('Inductive:')
            print(end_time - start_time)
            gviz = apply(net, initial_marking=initial_marking, final_marking=final_marking)
            save(gviz, os.path.join(data_set_paths[i], tau_sub_folder, 'INDUCTIVE', result_folder, 'net.png'))
            evaluate_net(log, net, initial_marking, final_marking, 
                os.path.join(data_set_paths[i], tau_sub_folder, 'INDUCTIVE', result_folder)
            )

            net, initial_marking, final_marking = alpha_miner.apply(log)
            gviz = apply(net, initial_marking=initial_marking, final_marking=final_marking)
            save(gviz, os.path.join(data_set_paths[i], tau_sub_folder, 'ALPHA', result_folder, 'net.png'))
            evaluate_net(log, net, initial_marking, final_marking, os.path.join(data_set_paths[i], tau_sub_folder, 'ALPHA', result_folder))

if __name__ == "__main__":
    execute_experiments()

