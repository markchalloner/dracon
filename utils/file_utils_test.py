import os
import unittest
import tempfile
import shutil
from gen import engine_pb2
from utils.file_utils import load_files


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        scan_results = engine_pb2.LaunchToolResponse(
            scan_info=engine_pb2.ScanInfo(
                scan_uuid='dd1794f2-544d-456b-a45a-a2bec53633b1',
            ),
            tool_name='bandit',
        )
        self.tmp_root_dir = tempfile.mkdtemp()
        _, self.tmpfile = tempfile.mkstemp(
            suffix=".pb", prefix="example_response_", dir=self.tmp_root_dir)
        with open(self.tmpfile, "wb") as f:
            serialized_proto = scan_results.SerializeToString()
            f.write(serialized_proto)

        # Duplicate the serialized protobuf into a subfolder to check recursion
        self.tmp_subdir = tempfile.mkdtemp(dir=self.tmp_root_dir)
        _, self.tmpfile2 = tempfile.mkstemp(
            suffix=".pb", prefix="example_response_copy_", dir=self.tmp_subdir)
        with open(self.tmpfile2, "wb") as f:
            serialized_proto = scan_results.SerializeToString()
            f.write(serialized_proto)

        # Create a malformed protobuf to check we handle it gracefully
        malformed_proto = serialized_proto[10:]
        _, self.malformed = tempfile.mkstemp(
            suffix=".pb", prefix="malformed_", dir=self.tmp_root_dir)
        with open(self.malformed, "wb") as f:
            f.write(malformed_proto)

        print(self.tmp_root_dir,self.tmp_subdir,self.tmpfile,self.tmpfile2,self.malformed)

    def tearDown(self):
        shutil.rmtree(self.tmp_root_dir)

    def test_proto_read(self):
        '''Test we can load protos and read from them correctly
           Also ensures we handled malformed protobufs gracefully
        '''
        scan_result_proto = engine_pb2.LaunchToolResponse()
        collected_results = load_files(scan_result_proto, self.tmp_root_dir)
        result = collected_results.pop()

        self.assertEqual(result.scan_info.scan_uuid,
                         'dd1794f2-544d-456b-a45a-a2bec53633b1')

    def test_file_search(self):
        '''Check that the recursive file detection is working as expected'''
        scan_result_proto = engine_pb2.LaunchToolResponse()
        collected_results = load_files(scan_result_proto, self.tmp_root_dir)
        self.assertEqual(len(collected_results), 2)

if __name__ == '__main__':
    unittest.main()
