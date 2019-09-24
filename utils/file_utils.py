import copy

from pathlib import Path
import logging
from google.protobuf.message import DecodeError

logger = logging.getLogger(__name__)


def load_files(protobuf, location):
    """Given a protobuf object and a filesystem location, attempts to load all *.pb
       files found in directories underneath the location into the protobuf object

       :param protobuf: object expected to be found in the location
       :param location: directory where protobuf objects are stored

       :returns array of protobuf objects of the given type which were found at the location
       :raise SyntaxError: If there are no .pb files found in location
    """

    logger.info('Searching for scan results')
    collected_files = []

    for filename in  Path(location).glob('**/*.pb'):
        logger.info("Found file %s" % filename)
        with open(filename, "rb") as f:
            try:
                protobuf.ParseFromString(f.read())
                collected_files.append(copy.deepcopy(protobuf))

            except DecodeError as e:
                logger.warning('Unable to parse file %s skipping because of: %s '%(filename,str(e)))
                # Note: here skipping is important,
                #  the results dir might have all sorts of protobuf messages that don't
                #  match the type provided
    if len(collected_files) == 0:
        raise SyntaxError('No valid results were found in the provided directory')

    return collected_files
