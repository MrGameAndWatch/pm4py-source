import numpy as np
import matplotlib.pyplot as plt
import os

from experiments.logging.logger import RuntimeStatisticsLogger

def plot_runtimes(stat_logger, path):
    runtimes = (
        stat_logger.algo_runtime(unit='ms'), 
        stat_logger.search_runtime(unit='ms'),
        stat_logger.replay_runtime(unit='ms'),
        stat_logger.post_processing_runtime(unit='ms')
    )

    index = np.arange(len(runtimes))

    plt.bar(index, runtimes, align='center')
    plt.xlabel('Phase')
    plt.ylabel('Time (ms)')
    plt.title('Runtime by Phases')
    plt.xticks(index, ('Algo', 'Search', 'Replay', 'Post-Proc.'))

    plt.savefig(path)
    plt.close()

def plot_pruned_places(stat_logger, path):
    blue_pruned_places  = stat_logger.num_pruned_blue_places()
    red_pruned_places   = stat_logger.num_pruned_red_places()
    total_pruned_places = stat_logger.total_pruned_places()

    pruned_places = (
        total_pruned_places,
        blue_pruned_places,
        red_pruned_places
    )

    index = np.arange(3)

    plt.bar(index, pruned_places, align='center')
    plt.xlabel('Edge Type')
    plt.ylabel('Number')
    plt.title('Pruned Places')
    plt.xticks(index, ('All', 'Blue', 'Red'))

    plt.savefig(os.path.join(path))
    plt.close()
