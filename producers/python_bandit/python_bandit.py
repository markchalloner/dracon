#!/usr/bin/env python3

import importlib
import os
import sys
import logging
import argparse
from collections import namedtuple

from producers.producer import Producer
from utils import dracon_exceptions


from bandit.core import config as b_config
from bandit.core import manager as b_manager
from bandit.core import extension_loader

logger = logging.getLogger(__name__)


class BanditProducer(Producer):
    target = None
    manager = None

    def setup_from_argparse(self, tool_conf: argparse.Namespace) -> bool:
        try:
            self.target = super().load_config_from_arguments(tool_conf)
        except dracon_exceptions.DraconConfigError:
            return False
        return True

    def setup_from_file(self, fpath: str = '/tmp/launchToolRequest.pb') -> bool:
        try:
            self.target = super().load_config_from_file(fpath)
            return True
        except dracon_exceptions.DraconConfigError:
            return False

    def setup(self, tool_conf) -> bool:
        """
        Setup a bandit producer. Initialize target, output and scan_uuid
        and prepare manager to be used.
        :param tool_conf: config passed through argparse
        :returns True if setup is done correctly, False in case of error
        """
        
        if (not self.setup_from_argparse(tool_conf) and
                not self.setup_from_file()):
            logger.fatal("Arguments couldnt be loaded")
            raise dracon_exceptions.DraconConfigError(
                "Could not configure Producer")

        # setup bandit
        logger.debug("setup bandit instance")
        bandit_conf = b_config.BanditConfig()
        self.manager = b_manager.BanditManager(bandit_conf, 'file')
        self.manager.discover_files([self.target], True)

        logger.debug("bandit setup, checking if tests are set.")
        if not self.manager.b_ts.tests:
            logger.info('No tests would be run, please check the profile.')
            return False

        return True

    def write_output(self, issues: list) -> bool:
        """
            Calls ProducerTemplate.write_output to send output to
            PVC defined in self.output
        """
        return super().write_output('bandit', issues)

    def convert_to_issue(self, rec_issue: dict):
        """
            Convert a dict issues to a proto Issue object
            using ProducerTemplate

            :param rec_issue: issue as a dictionary
            :return issue as a proto object
        """
        plugin_info = extension_loader.MANAGER.plugins_by_id
        blacklist_info = {} #blacklist means dangerous blacklisted methods

        for a in extension_loader.MANAGER.blacklist.items():
            for b in a[1]:
                blacklist_info[b['id']]=b

        plugin_info.update(blacklist_info)
        
        return super().convert_to_issue({
            'target': f"{rec_issue['filename']}:{rec_issue['line_range']}",
            'type': plugin_info[rec_issue['test_id']]['name'],
            'title': plugin_info[rec_issue['test_id']]['name'],
            'severity': f"SEVERITY_{rec_issue['issue_severity']}",
            "cvss": 0,
            'confidence': f"CONFIDENCE_{rec_issue['issue_confidence']}",
            'description': rec_issue['issue_text']
        })

    def run(self) -> list:
        """
            Run the tests and construct a list of issues

            :return list of issues as proto objects
        """
        self.manager.run_tests()

        to_report = []
        for r in self.manager.results:
            to_report.append(self.convert_to_issue(r.as_dict()))

        return to_report


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', help='output file')
    parser.add_argument('--target', help='target to verify')
    parser.add_argument('--scan_uuid', help='scan uuid')
    parser.add_argument('--ts', help='time when the scan was triggered')
    # @todo(spyros): implement transparent arg parsing to bandit
    # parser.add_argument('toolArgs',default='', help='(not supported) extra arguments you want to pass bandit')
    args = parser.parse_args()

    logger.debug("creating producer")
    bproducer = BanditProducer()
    if not bproducer.setup(args):
        sys.exit(2)
    logger.debug("executing bandit")
    issues = bproducer.run()
    logger.debug("producing output.")
    bproducer.write_output(issues)
    logger.debug("output written, terminating normally.")
