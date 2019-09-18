import glob
import os
import unittest
from base64 import b64encode
from unittest import mock
from datetime import datetime

from utils import db_utils as db
from utils.producer_test_utils import get_random_str
from gen import engine_pb2
from gen import issue_pb2
from enrichment_service.enrichment_service import EnrichmentService
from google.protobuf.timestamp_pb2 import Timestamp
from enrichment_service import enrichment_service


class TestEnrichment(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = {
            'read_pvc_location': './read/',
            'write_pvc_location': './write/',
            'db_uri': "postgres://username@hostname/databasename"
        }

    def generate_tool_response(self):
        ts = Timestamp()
        ts.FromJsonString("1991-01-01T00:00:00Z")
        scan_results = engine_pb2.LaunchToolResponse(
            scan_info=engine_pb2.ScanInfo(
                scan_uuid='dd1794f2-544d-456b-a45a-' + util_test.get_random_str(12),
                scan_start_time=ts,
            ),
            tool_name=util_test.get_random_str(5),
        )
        self.scan_uuids.append(scan_results.scan_info.scan_uuid)
        return scan_results

    def generate_issue(self):
        issue = issue_pb2.Issue()
        issue.target = util_test.get_random_str(10)
        issue.type = util_test.get_random_str(10)
        issue.title = util_test.get_random_str(10)
        issue.severity = issue_pb2.SEVERITY_CRITICAL
        issue.cvss = 19.01234
        issue.confidence = issue_pb2.CONFIDENCE_HIGH
        issue.description = util_test.get_random_str(10)
        return issue

    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.connect")
    def setUp(self, mock_connect):
        self.test_scan_results = []
        self.scan_uuids = []
        self.issue_hashes = []
        self.duplicate_hash = {}
        service = EnrichmentService(self.config)
        for el in range(5):
            # Create a scan results object and serialize it to a file
            ts = Timestamp()
            ts.FromJsonString("1991-01-01T00:00:0" + str(el) + "Z")
            scan_results = self.generate_tool_response()

            # assure we have a predictable issue in our results we can use for searching
            issue = issue_pb2.Issue()
            issue.target = 'target.py:' + str(el)
            issue.type = "Test_Type"
            issue.title = "Test_Title"
            issue.severity = issue_pb2.SEVERITY_CRITICAL
            issue.cvss = 19.01234 + el
            issue.confidence = issue_pb2.CONFIDENCE_HIGH
            issue.description = "Test_Description"
            scan_results.issues.extend([issue])
            scan_results.issues.extend([issue])  # assure we have a duplicate, predictably enriched
            self.duplicate_hash[service._md5_hash(issue)] = issue
            # should have a counter of 2
            # then generate some noise to make sure the rest of the engine works as expected
            for _ in range(10 + el):
                scan_results.issues.extend([self.generate_issue()])

            self.test_scan_results.append(scan_results)  # safekeeping

            filename = self.config['read_pvc_location'] + "/example_simple_response"
            filename = filename + scan_results.scan_info.scan_uuid + ".pb"

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                scan_proto_string = scan_results.SerializeToString()
                f.write(scan_proto_string)

    def special_issue_by_hash(self, issue_hash):
        if issue_hash in self.duplicate_hash.keys():
            iss = self.duplicate_hash[issue_hash]
            return {
                'type': iss.type,
                'target': iss.target,
                'title': iss.title,
                'severity': iss.severity,
                'cvss': iss.cvss,
                'confidence': iss.confidence,
                'description': iss.description,
                'hash': issue_hash,
                'found_counter': 1,
                'first_seen': datetime.utcnow()
            }
        else:
            return {}

    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.insert_issue")
    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.increase_count")
    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.get_issue_by_hash")
    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.connect")
    def test_enrichment(self, mock_connect, mock_get_issue_by_hash,
                        mock_increase_count, mock_insert_issue):
        """A basic test that reads a scan result, enriches it, and ensures that it's
           enriched as we might expect

            enrich all results in read_pvc_location
           for every scan in self.test_scan_results:
                assert original issues exist in enriched pile
           """
        mock_get_issue_by_hash.side_effect = self.special_issue_by_hash

        enricher = EnrichmentService(self.config)
        enriched_results = enricher.enrich_results()

        for enriched_tool_response in enriched_results:
            enriched_uuid = enriched_tool_response.original_results.scan_info.scan_uuid
            for launch_tool_response in self.test_scan_results:
                if launch_tool_response.scan_info.scan_uuid == enriched_uuid:
                    # non-enriched issues have a duplicate one on purpose
                    self.assertEqual(len(enriched_tool_response.issues),
                                     len(launch_tool_response.issues) - 1)

                    self.assert_issue_contents_match(enriched_issues=enriched_tool_response.issues,
                                                     original_issues=launch_tool_response.issues)

    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.insert_issue")
    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.increase_count")
    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.connect")
    @mock.patch("infrastructure.security.dracon.utils.db_utils.DraconDBHelper.get_issue_by_hash")
    def test_enriched_storage(self, mock_connect, mock_get_issue_by_hash,
                              increase_count, mock_insert_issue):
        """ Test that we can read stored enriched results correctly """
        mock_get_issue_by_hash.side_effect = self.special_issue_by_hash

        enricher = EnrichmentService(self.config)
        enriched_results = enricher.enrich_results()

        enricher.store_enriched_results(enriched_results)
        results_from_file = engine_pb2.EnrichedLaunchToolResponse()
        glob_pattern = self.config['write_pvc_location'] + '**/*.pb'
        for filename in glob.iglob(glob_pattern, recursive=True):
            with open(filename, "rb") as f:
                results_from_file.ParseFromString(f.read())
                self.assertIn(results_from_file.original_results.scan_info.scan_uuid,
                              self.scan_uuids)

    def assert_issue_contents_match(self, enriched_issues: issue_pb2.EnrichedIssue,
                                    original_issues: issue_pb2.Issue):
        e_issue_hashes = {}

        # we don't need to check every field of every issue,
        # protobufs are serializable, and base64 provides a unique representation of every string
        # if the base64 repr of an enriched issue's "Issue" field is the same as the b64 repr of
        # an Issue then their contents are the same.
        # This asserts that we didn't miss any unique issues in deduplication
        for e_issue in enriched_issues:
            e_issue_hashes[b64encode(e_issue.raw_issue.SerializeToString())] = e_issue

        for o_issue in original_issues:
            self.assertIn(b64encode(o_issue.SerializeToString()), e_issue_hashes.keys())


if __name__ == '__main__':
    unittest.main()
