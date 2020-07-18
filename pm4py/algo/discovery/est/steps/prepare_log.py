from pm4py.algo.discovery.est.log import log_transformation

def apply(log):
    log = log_transformation.add_unique_start_and_end_activity(log)
    log = log_transformation.transform_to_bitmasked_log(log)
    return log
