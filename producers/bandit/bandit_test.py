#!/usr/bin/env python3

import os
import unittest
import tempfile

from gen import engine_pb2
from gen import issue_pb2
from gen import config_pb2
from producers.bandit.bandit import BanditProducer
from producers.producer_test_utils import MockConfig

from google.protobuf.timestamp_pb2 import Timestamp
from utils.dracon_exceptions import DraconConfigError


tmp_conf = MockConfig()
tmp_conf.scan_uuid = None
tmp_conf.scan_start_time = "1991-01-01T00:00:00Z"
tmp_conf.output = None
tmp_conf.target = None

EMPTY_CONFIG = tmp_conf
VALID_CONFIG = MockConfig()


class TestBanditProducer(unittest.TestCase):
    bandit_producer = None
    issue = {
        "code": "316                 )\n317         except:\n318             pass\n",
        "filename": "/home/someone/core/common/python/zipkin/zipkin.py",
        "issue_confidence": "HIGH",
        "issue_severity": "LOW",
        "issue_text": "Try, Except, Pass detected.",
        "line_number": 317,
        "line_range": [
            317
        ],
        "test_id": "B110",
        "test_name": "try_except_pass"
    }

    def setUp(self):
        self.test_path = tempfile.mkdtemp()
        VALID_CONFIG.target = self.test_path
        self.valid_config = VALID_CONFIG

    def _write_test_pb(self):
        """
            auxiliary method to write a valid protobuf file with a request
        """

        ts = Timestamp()
        ts.FromJsonString(VALID_CONFIG.ts)

        scan_info = engine_pb2.ScanInfo(
            scan_uuid=VALID_CONFIG.scan_uuid,
            scan_start_time=ts
        )

        wrapper_args = config_pb2.WrapperArgs(
            target=VALID_CONFIG.target,
            output=VALID_CONFIG.output
        )

        config = config_pb2.Config(
            wrapperArgs=wrapper_args,
            toolArgs={}
        )

        ltr = engine_pb2.LaunchToolRequest(
            scan_info=scan_info,
            config=config
        )

        with open(f"{self.test_path}/launchToolRequest.pb", 'wb') as f:
            f.write(ltr.SerializeToString())

    def _create_producer(self):
        """
            auxiliary method to create a base producer using valid values
        """

        bandit_producer = BanditProducer()
        bandit_producer.setup(VALID_CONFIG)
        return bandit_producer

    def test_setup_by_pb_file(self):
        """
            Test if it's possible to start a Bandit Producer using config
            from a protobuf file
        """

        self._write_test_pb()

        bandit_producer = BanditProducer()
        self.assertTrue(bandit_producer.setup_from_file(
            f"{self.test_path}/launchToolRequest.pb"))
        self.assertEqual(bandit_producer.target, VALID_CONFIG.target)

        os.remove(f'{self.test_path}/launchToolRequest.pb')

    def test_setup_via_config(self):
        """
            Test if it's possible to start a Bandit Producer using
            config from command line arguments
        """

        bandit_producer = BanditProducer()
        self.assertTrue(bandit_producer.setup(VALID_CONFIG))
        self.assertEqual(bandit_producer.target, VALID_CONFIG.target)

    def test_fail_cmd_config(self):
        """
            Test if it's trying to start a Bandit Producer using
            an invalid config from command line arguments returns error
        """

        config = MockConfig()
        config.ts = None
        config.scan_uuid = None

        bandit_producer = BanditProducer()
        self.assertRaises(DraconConfigError,
                          lambda: bandit_producer.setup(config))

    def test_fail_pb_config(self):
        """
            Test if it's trying to start a Bandit Producer using
            an invalid config from a read protobuf file returns error
        """

        ts = Timestamp()
        ts.FromJsonString(VALID_CONFIG.ts)

        scan_info = engine_pb2.ScanInfo(
            scan_uuid="",
            scan_start_time=ts
        )

        wrapper_args = config_pb2.WrapperArgs(
            target=VALID_CONFIG.target,
            output=VALID_CONFIG.output
        )

        config = config_pb2.Config(
            wrapperArgs=wrapper_args,
            toolArgs={}
        )

        ltr = engine_pb2.LaunchToolRequest(
            scan_info=scan_info,
            config=config
        )

        with open(f'{self.test_path}/launchToolRequest.pb', 'wb') as f:
            f.write(ltr.SerializeToString())

        bandit_producer = BanditProducer()
        self.assertRaises(DraconConfigError,
                          lambda: bandit_producer.setup(EMPTY_CONFIG))

        os.system(f'rm {self.test_path}/launchToolRequest.pb')

    def test_load_plugins(self):
        """
            Test if loading the bandit plugins is working
        """

        bandit_producer = self._create_producer()
        self.assertTrue(list(bandit_producer._load_bandit_plugins()))

    def test_convert_issue(self):
        """
            Test converting a bandit issue to a Dracon Issue
            in protobuf format
        """

        bandit_producer = self._create_producer()
        issue = bandit_producer.convert_to_issue(self.issue)

        self.assertEqual(
            issue.target, f"{self.issue['filename']}:{self.issue['line_range']}")
        self.assertEqual(issue.type, 'try_except_pass')
        self.assertEqual(issue.title, 'try_except_pass')
        self.assertEqual(issue.severity, issue_pb2.SEVERITY_LOW)
        self.assertEqual(issue.cvss, 0)
        self.assertEqual(issue.confidence, issue_pb2.CONFIDENCE_HIGH)
        self.assertEqual(issue.description, self.issue['issue_text'])

    def test_convert_invalid_issue(self):
        """
            Test converting an invalid bandit issue to a Dracon Issue
        """

        bandit_producer = self._create_producer()

        issue_cp = self.issue.copy()
        issue_cp['issue_severity'] = "TEST"
        self.assertRaises(
            ValueError, lambda: bandit_producer.convert_to_issue(issue_cp))

        issue_cp = self.issue.copy()
        del issue_cp['filename']
        self.assertRaises(
            KeyError, lambda: bandit_producer.convert_to_issue(issue_cp))

    def test_write_output(self):
        """
            Test writing output to the file passed during config
        """

        bandit_producer = self._create_producer()

        proto_issue = bandit_producer.convert_to_issue(self.issue)
        self.assertTrue(bandit_producer.write_output([proto_issue]))

    def test_run(self):
        """
            Test normal bandit run
        """

        bandit_producer = self._create_producer()
        res = bandit_producer.run()
        self.assertIsInstance(res, list)


if __name__ == '__main__':
    unittest.main()
