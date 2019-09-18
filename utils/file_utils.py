import copy
import glob

from common.python.logging.config import get_logger
from google.protobuf.message import DecodeError

logger = get_logger(__name__)


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

    for filename in glob.iglob(location + '**/*.pb', recursive=True):
        logger.info("Found file %s" % filename)
        f = open(filename, "rb")
        try:
            protobuf.ParseFromString(f.read())
            collected_files.append(copy.deepcopy(protobuf))

        except DecodeError as e:
            logger.warning('Unable to parse file, skipping: ' + filename + str(e))

    if len(collected_files) == 0:
        raise SyntaxError('No valid results were found in the provided directory')

    return collected_files
