#!/usr/bin/env python3


import os
import re
import logging

from abc import ABC
from gen import engine_pb2
from gen import issue_pb2
from utils import dracon_exceptions
from google.protobuf.timestamp_pb2 import Timestamp


logger = logging.getLogger(__name__)

class Producer(ABC):
    output = None
    scan_uuid = None
    scan_start_time = None
    target = None

    def _check_config_is_valid(self, conf_args: dict) -> bool:
        """
            Performs a series of checks over conf_args, to check if this
            can be used to setup a Producer

            :param conf_args: dictionary containing LaunchToolRequest parameters
            :returns True if the config is valid, False otherwise
        """

        if (not conf_args['scan_uuid'] or
                not conf_args['scan_start_time'] or
                not conf_args['output'] or
                not conf_args['target']):
            logger.error("Incomplete config information provided.")
            return False
        elif not os.access(os.path.dirname(conf_args['output']), os.W_OK):
            logger.error("Cant write to output file %s"%conf_args['output'])
            return False
        elif not re.match(
                r'^[a-f\d]{8}-[a-f\d]{4}-4[a-f\d]{3}-[89ab][a-f\d]{3}-[a-f\d]{12}$',  # NOQA
                conf_args['scan_uuid']
        ):
            logger.error("UUID does not have the right format")
            return False

        return True

    def _set_config(self, conf_args: dict) -> str:
        """
            Check if the config dictionary is valid and if so, initialize
            the class variables

            :param conf_args: dictionary containing LaunchToolRequest parameters
            :returns the provided target
        """

        if not self._check_config_is_valid(conf_args):
            raise dracon_exceptions.DraconConfigError

        self.scan_uuid = conf_args['scan_uuid']
        self.scan_start_time = conf_args['scan_start_time']
        self.output = conf_args['output']
        self.target = conf_args['target']

        return self.target

    # @todo(spyros) : we're raising exceptions for optional config missing, refactor
    def load_config_from_file(self, fpath: str) -> str:
        """
            Read LaunchToolRequest object from a file and return
            as an object

            :param fpath: Location of the configuration file
            :returns Producer Target
        """

        ltr = engine_pb2.LaunchToolRequest()
        try:
            with open(fpath, 'rb') as f:
                content = f.read()
        except FileNotFoundError as e:
            logger.debug("LaunchToolRequest not found.")
            logger.debug(e)
            raise dracon_exceptions.DraconConfigError
        except IOError as e:
            logger.info("Error retrieving LaunchToolRequest from file.")
            logger.debug(e)
            raise dracon_exceptions.DraconConfigError

        if ltr.ParseFromString(content) == 0:
            raise dracon_exceptions.DraconConfigError('Cant parse LaunchToolRequest file')

        return self._set_config({'scan_uuid': ltr.scan_info.scan_uuid,
                                 'scan_start_time': ltr.scan_info.scan_start_time,
                                 'output': ltr.config.wrapperArgs.output,
                                 'target': ltr.config.wrapperArgs.target})

    def load_config_from_arguments(self, conf_args: Namespace) -> str:
        """
            Load LaunchToolRequest object from command line arguments

            :param conf_args: argpase Namespace containing configuration arguments
            :returns Producer Target
        """
        try:
            timestamp = Timestamp()
            timestamp.FromJsonString(conf_args.ts)
        except AttributeError:
            logger.error("conf_args.scan_start_time is illegal")
            timestamp = None
        return self._set_config({'scan_uuid': conf_args.scan_uuid,
                                 'scan_start_time': timestamp,
                                 'output': conf_args.output,
                                 'target': conf_args.target})

    def write_output(self, tool: str, issues: list) -> bool:
        """
            Write list of protos to output file as serialized proto

            :param tool: name of tool producing the output
            :param issues: found issues to upload
            :return True if write succeeded, false otherwise
        """
        ltr = engine_pb2.LaunchToolResponse(
            scan_info=engine_pb2.ScanInfo(
                scan_uuid=self.scan_uuid,
                scan_start_time=self.scan_start_time
            ),
            tool_name=tool,
            issues=issues
        )

        with open(self.output, 'ab') as f:
            if f.write(ltr.SerializeToString()) == 0:
                raise dracon_exceptions.DraconOutputError(
                    'Possible to open file, but not write. output'
                )

        return True

    def convert_to_issue(self, rec_issue) -> issue_pb2.Issue:
        """
            Convert a dict issues to a proto Issue object

            :param rec_issue: issue as a dictionary
            :return issue as a proto object
        """
        return issue_pb2.Issue(**rec_issue)
