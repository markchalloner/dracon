#!/usr/bin/env python3

import gflags
import importlib
import os
import sys

from collections import namedtuple

from common.python import flag_utils
from .. import Producer
from ..utils import dracon_exceptions


from bandit.core import config as b_config
from bandit.core import manager as b_manager
from bandit.core import extension_loader

FLAGS = gflags.FLAGS

gflags.DEFINE_string('output', None, 'output file')
gflags.DEFINE_string('target', None, 'target to verify')
gflags.DEFINE_string('scan_uuid', None, 'scan uuid')
gflags.DEFINE_string('ts', None, 'time when the scan was triggered')

logger = get_logger(__name__)


class BanditProducer(Producer):
    target = None
    manager = None

    def _load_bandit_plugins(self, dirname='third_party/python3/bandit/plugins'):
        '''
            Manually load bandit plugins. This is required due to how plz packages
            wheels.
        '''
        plugin = namedtuple('Plugin', ['name', 'plugin'])
        for filename in os.listdir(dirname):
            if filename.endswith('.py') and filename != '__init__.py':
                package_name = os.path.join(dirname, filename[:-3]).replace('/', '.')
                module = importlib.import_module(package_name)
                for k, v in module.__dict__.items():
                    if hasattr(v, '_test_id'):
                        yield plugin(filename[:-3], v)

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
            raise dracon_exceptions.DraconConfigError("Could not configure Producer")

        # setup bandit
        logger.debug("setup bandit instance")
        bandit_conf = b_config.BanditConfig()

        logger.debug("Loading plugin ids to set tests")
        mgr = extension_loader.MANAGER
        mgr.plugins = list(self._load_bandit_plugins())
        mgr.plugin_names = [plugin.name for plugin in mgr.plugins]
        mgr.plugins_by_id = {p.plugin._test_id: p for p in mgr.plugins}  # noqa
        mgr.plugins_by_name = {p.name: p for p in mgr.plugins}

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

        return super().convert_to_issue({
            'target': f"{rec_issue['filename']}:{rec_issue['line_range']}",
            'type': extension_loader.MANAGER.plugins_by_id[rec_issue['test_id']].name,
            'title': extension_loader.MANAGER.plugins_by_id[rec_issue['test_id']].name,
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
    flag_utils.parse_flags()
    logger.debug("creating producer")
    bproducer = BanditProducer()
    if not bproducer.setup(FLAGS):
        sys.exit(2)
    logger.debug("executing bandit")
    issues = bproducer.run()
    logger.debug("producing output.")
    bproducer.write_output(issues)
    logger.debug("output written, terminating normally.")
