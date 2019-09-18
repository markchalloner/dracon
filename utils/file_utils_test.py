import os
import unittest

from infrastructure.security.dracon.proto import engine_pb2
from infrastructure.security.dracon.utils.file_utils import load_files


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        scan_results = engine_pb2.LaunchToolResponse(
            scan_info=engine_pb2.ScanInfo(
                scan_uuid='dd1794f2-544d-456b-a45a-a2bec53633b1',
            ),
            tool_name='bandit',
        )

        f = open("example_response.pb", "wb")
        serialized_proto = scan_results.SerializeToString()
        f.write(serialized_proto)
        f.close()

        # Duplicate the serialized protobuf into a subfolder to check recursion
        os.system('mkdir subfolder')
        os.system('cp example_response.pb subfolder/example_response_2.pb')

        # Create a malformed protobuf to check we handle it gracefully
        malformed_proto = serialized_proto[10:]
        f = open("malformed_response.pb", "wb")
        f.write(malformed_proto)
        f.close()

    def test_proto_read(self):
        '''Test we can load protos and read from them correctly
           Also ensures we handled malformed protobufs gracefully
        '''
        scan_result_proto = engine_pb2.LaunchToolResponse()
        collected_results = load_files(scan_result_proto, "./")
        result = collected_results.pop()

        self.assertEqual(result.scan_info.scan_uuid, 'dd1794f2-544d-456b-a45a-a2bec53633b1')

    def test_file_search(self):
        '''Check that the recursive file detection is working as expected'''
        scan_result_proto = engine_pb2.LaunchToolResponse()
        collected_results = load_files(scan_result_proto, "./")
        self.assertEqual(len(collected_results), 2)
