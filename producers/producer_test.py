#!/usr/bin/env python3

import os
import tempfile
import unittest
from google.protobuf.timestamp_pb2 import Timestamp

from utils import dracon_exceptions
from producers.producer import Producer
from gen import engine_pb2
from gen import issue_pb2
from gen import config_pb2
from utils import test_utils

VALID_CONFIG = test_utils.ProducerMockConfig()

class TestProducer(unittest.TestCase):
    producer_template = None

    issue = {
        'target': '/some/long/pAtH/which-cont4ins/st_u_ff/web_server.py:[58]',
        'type': 'general_bind_all_interfaces',
        'title': 'general_bind_all_interfaces',
        'severity': 'SEVERITY_MEDIUM',
        'cvss': 0,
        'confidence': 'CONFIDENCE_MEDIUM',
        'description': 'Possible binding to all interfaces.'
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

        with open(f'{self.test_path}/launchToolRequest.pb', 'wb') as f:
            f.write(ltr.SerializeToString())

    def test_setup_by_pb_file(self):
        """
            Test creating a producer from a LaunchToolRequest protobuf file
        """

        self._write_test_pb()
        producer = Producer()

        self.assertEqual(
            producer.load_config_from_file(self.test_path + "/launchToolRequest.pb"),
            self.valid_config.target
        )
        self.assertEqual(producer.scan_uuid, VALID_CONFIG.scan_uuid)
        self.assertEqual(producer.output, VALID_CONFIG.output)

        ts = Timestamp()
        ts.FromJsonString(VALID_CONFIG.ts)
        self.assertEqual(producer.scan_start_time, ts)

        os.remove(f'{self.test_path}/launchToolRequest.pb')

    def test_valid_set_config(self):
        """
            Test creating a producer using command line arguments
        """

        timestamp = Timestamp()
        timestamp.FromJsonString(VALID_CONFIG.ts)
        config = {'scan_uuid': VALID_CONFIG.scan_uuid,
                  'scan_start_time': timestamp,
                  'output': VALID_CONFIG.output,
                  'target': VALID_CONFIG.target
                  }

        producer = Producer()
        self.assertTrue(producer._set_config(config))

    def test_invalid_set_config(self):
        """
            Test creating a producer using invalid command line arguments
        """

        producer = Producer()
        timestamp = Timestamp()
        timestamp.FromJsonString(VALID_CONFIG.ts)
        config = {'scan_uuid': VALID_CONFIG.scan_uuid,
                  'scan_start_time': timestamp,
                  'output': VALID_CONFIG.output,
                  'target': VALID_CONFIG.target
                  }

        invalid_conf_none_val = config.copy()
        invalid_conf_none_val['scan_uuid'] = None

        invalid_conf_target = config.copy()
        invalid_conf_target['target'] = "/nonexistant/target/"

        invalid_conf_start_time = config.copy()
        invalid_conf_start_time['scan_start_time'] = ""

        inaccessible_file = config.copy()
        inaccessible_file['target'] = '/etc/shadow'  # guaranteed unreadable,
        # if readable we really need to know about it

        unwritable_dir = config.copy()
        unwritable_dir['output'] = '/root/'  # guaranteed unwritable
        # if writable we have a problem

        bad_uuid = config.copy()
        bad_uuid['scan_uuid'] = 'this-is-not-a-valid-uuid-??!@#$!@#'

        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: producer._set_config(invalid_conf_none_val)
        )
        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: producer._set_config(invalid_conf_start_time)
        )
        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: producer._set_config(unwritable_dir)
        )
        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: producer._set_config(bad_uuid)
        )

    def test_load_invalid_file(self):
        """
            Test if it's trying to start a Producer
            using invalid values:
            - load an invalid config file
            - load an inexistant config file
        """

        # setup
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

        with open(f'{self.test_path}launchToolRequest.pb', 'wb') as f:
            f.write(ltr.SerializeToString()[100:124])  # make file invalid

        producer = Producer()

        # Try to load using an invalid config file
        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: producer.load_config_from_file(f'{self.test_path}/launchToolRequest.pb')
        )

        # Try to load from a config that doesnt exist
        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: Producer().load_config_from_file("/this/path/should/not/exist/nothing.pb")
        )

        # Try to load from a file that can't be read
        # if this fails we have other problems
        self.assertRaises(
            dracon_exceptions.DraconConfigError,
            lambda: Producer().load_config_from_file("/etc/shadow")
        )

    def _create_producer(self):
        """
            auxiliary method to create a base producer using valid values
        """

        producer_template = Producer()
        producer_template.load_config_from_arguments(VALID_CONFIG)
        return producer_template

    def test_convert_to_issue(self):
        """
            Test converting a bandit issue to a Dracon Issue
            in protobuf format
        """

        producer_template = self._create_producer()
        issue = producer_template.convert_to_issue(self.issue)

        self.assertEqual(issue.target, self.issue['target'])
        self.assertEqual(issue.type, self.issue['type'])
        self.assertEqual(issue.title, self.issue['title'])
        self.assertEqual(issue.severity, issue_pb2.SEVERITY_MEDIUM)
        self.assertEqual(issue.cvss, 0)
        self.assertEqual(issue.confidence, issue_pb2.CONFIDENCE_MEDIUM)
        self.assertEqual(issue.description, self.issue['description'])

    def test_convert_invalid_issue(self):
        """
            Test converting an invalid issue to a Dracon Issue
        """

        producer = self._create_producer()

        # provide wrong enum
        issue_cp = self.issue.copy()
        issue_cp['issue_severity'] = "TEST"
        self.assertRaises(ValueError, lambda: producer.convert_to_issue(issue_cp))

    def test_write_output_error(self):
        """
            Test writing to an invalid location
        """

        producer = self._create_producer()
        producer.output = "/I_cant_write_here/inexistent_path/"

        proto_issue = producer.convert_to_issue(self.issue)
        self.assertRaises(FileNotFoundError, lambda: producer.write_output(
            'bandit',
            [proto_issue]
        ))

    def test_write_output(self):
        """
            Test writing output to the file passed during config
        """

        producer_template = self._create_producer()
        proto_issue = producer_template.convert_to_issue(self.issue)
        self.assertTrue(producer_template.write_output(
            'bandit',
            [proto_issue]
        ))

        ltr = engine_pb2.LaunchToolResponse()
        with open(VALID_CONFIG.output, 'rb') as f:
            ltr.ParseFromString(f.read())

        self.assertEqual(ltr.scan_info.scan_uuid, producer_template.scan_uuid)
        self.assertEqual(ltr.scan_info.scan_start_time, producer_template.scan_start_time)
        self.assertEqual(ltr.tool_name, 'bandit')
        self.assertEqual(ltr.issues[0], proto_issue)


if __name__ == '__main__':
    unittest.main()
