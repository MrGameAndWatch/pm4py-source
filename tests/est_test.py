import logging
import os
import unittest

from pm4py.objects.log import log as event_log
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.util import xes_constants
from pm4py.objects.log.util import log as log_util
from tests.constants import INPUT_DATA_DIR

from pm4py.algo.discovery.est.log import log_transformation

class EstLogTransformerTest(unittest.TestCase):

    def test_logHasUniqueStartAndEndActivity(self):
        log = xes_importer.apply(os.path.join(os.path.dirname(__file__), INPUT_DATA_DIR, "running-example.xes"))
        initial_activities = set(log_util.get_event_labels(log, xes_constants.DEFAULT_NAME_KEY))

        obtained_log = log_transformation.add_unique_start_and_end_activity(log)

        expected_start = event_log.Event({xes_constants.DEFAULT_NAME_KEY: '[start>'})
        expected_end = event_log.Event({xes_constants.DEFAULT_NAME_KEY: '[end]'})
        for trace in obtained_log:
            self.assertNotIn(trace.__getitem__(0), initial_activities)
            self.assertNotIn(trace.__getitem__(len(trace) - 1), initial_activities)
            self.assertEqual(trace.__getitem__(0), expected_start)
            self.assertEqual(trace.__getitem__(len(trace) - 1), expected_end)

    def test_logCorrectlyTransformedToBitmaskBasedLog(self):
        log = xes_importer.apply(os.path.join(os.path.dirname(__file__), INPUT_DATA_DIR, "running-example.xes"))
        bitmasked_log = log_transformation.transform_to_bitmasked_log(log)
        for i in range(len(log)):
            self.assertEqual(len(log.__getitem__(i)), len(bitmasked_log.__getitem__(i)))
