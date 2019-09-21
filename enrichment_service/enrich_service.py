import argparse
import hashlib

import os
import sys
import logging
import utils.db_utils as db

from gen import engine_pb2, issue_pb2
from utils.file_utils import load_files

logger = logging.getLogger(__name__)

class EnrichmentService():
    
    def __init__(self, config):
        try:
            self.read_pvc_location = config['read_pvc_location']
            self.write_pvc_location = config['write_pvc_location']
            self.db_uri = config['db_uri']
            self.dracon_db = db.DraconDBHelper()
            self.dracon_db.connect(self.db_uri)
        except KeyError:
            logger.error('PVC location or db_uri not provided')
            raise

    def _md5_hash(self, issue: issue_pb2.Issue):
        md = hashlib.md5()
        md.update(("" + issue.target + issue.type + issue.title).encode("ascii"))
        md.update(str(issue.severity).encode('ascii'))
        md.update(str(issue.cvss).encode('ascii'))
        md.update(str(issue.confidence).encode('ascii'))
        md.update(str(issue.description).encode('ascii'))
        return str(md.hexdigest())

    def enrich_single_issue(self, orig_issue: issue_pb2.Issue) -> (issue_pb2.EnrichedIssue, str):
        """ Given a single result returns an enriched result
        :return: tupple containing enriched result pb message and it's hash
        """
        enriched_issue = issue_pb2.EnrichedIssue()
        enriched_issue.raw_issue.CopyFrom(orig_issue)
        enriched_issue.false_positive = False

        issue_hash = self._md5_hash(orig_issue)
        issue = self.dracon_db.get_issue_by_hash(issue_hash)

        if len(issue) > 0:  # update count
            self.dracon_db.increase_count(issue_hash)
            enriched_issue.count = issue['found_counter'] + 1
            enriched_issue.first_seen.FromDatetime(issue['first_seen'])

            # @TODO(spyros) : implement fp handling by querying the changes table
        else:  # else enrich and insert
            enriched_issue.count = 1
            enriched_issue.first_seen.GetCurrentTime()

            self.dracon_db.insert_issue(target=orig_issue.target,
                                        title=orig_issue.title,
                                        severity=orig_issue.severity,
                                        cvss=orig_issue.cvss,
                                        confidence=orig_issue.confidence,
                                        description=orig_issue.description,
                                        hash=issue_hash,
                                        found_counter=enriched_issue.count,
                                        first_seen=enriched_issue.first_seen.ToJsonString())
        return enriched_issue, issue_hash

    def enrich_tool_response(self,
                             tool_response: engine_pb2.LaunchToolResponse = None) -> \
            engine_pb2.EnrichedLaunchToolResponse:
        """
        Given a single tool response with issues produce an enriched tool response
        :return: enriched tool response pb message
        """
        enriched_tool_results = engine_pb2.EnrichedLaunchToolResponse()
        enriched_issues = {}
        for issue in tool_response.issues:
            enriched_issue, issue_hash = self.enrich_single_issue(orig_issue=issue)
            enriched_issues[issue_hash] = enriched_issue

        enriched_tool_results.original_results.CopyFrom(tool_response)
        enriched_tool_results.issues.extend(enriched_issues.values())
        return enriched_tool_results

    def enrich_results(self) -> []:
        """
        Load a set of LaunchToolResponse protobufs, enrich them, and
        store them for a consumer to pick up in the future
        """
        scan_results = engine_pb2.LaunchToolResponse()
        collected_enriched_results = []
        collected_results = load_files(scan_results, self.read_pvc_location)

        for results in collected_results:  # loop over tool responses
            enriched_res = self.enrich_tool_response(tool_response=results)
            collected_enriched_results.append(enriched_res)
        return collected_enriched_results

    def store_enriched_results(self, results: list):
        """
        Takes a set of enriched scan results and stores it in the provided location
           :param results: List of EnrichedLaunchToolResponses
        """
        for result in results:
            raw_result = result.original_results

            # Uses the b64 encoded scan uuid as the filename for the result
            filepath = self.write_pvc_location + "/" + raw_result.scan_info.scan_uuid + '.pb'
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "wb") as f:
                logger.info('Writing enriched results to ' + filepath)
                serialized_result = result.SerializeToString()
                f.write(serialized_result)


def setup(db_uri):
    helper = db.DraconDBHelper()
    helper.connect(db_uri)
    for s in helper.generate_create_tables():
        helper.execute(s)


def main(stdin):
    parser = argparse.ArgumentParser()
    parser.add_argument('--read_pvc_location',
                        default=os.environ.get('DRACON_READ_PVC_LOCATION'),
                        help='The location which stores LaunchToolResponses')
    parser.add_argument('--write_pvc_location',
                        default=os.environ.get('DRACON_WRITE_PVC_LOCATION'),
                        help='The location to write enriched results to')
    parser.add_argument('--db_uri',
                        default=os.environ.get('DRACON_ENRICHMENT_DB_URI'),
                        help='The database connection string for persisting results')
    parser.add_argument('--setup', action="store_true",
                        default=os.environ.get('DRACON_ENRICHMENT_SETUP'),
                        help='Binary flag to run db migrations')

    args = vars(parser.parse_args())
    if args['setup'] is True:
        setup(args['db_uri'])

    try:
        enricher = EnrichmentService(args)
        collected_results = enricher.enrich_results()
        enricher.store_enriched_results(collected_results)
    except AttributeError as e:
        logger.error('A required argument is missing: ' + str(e))
        exit(1)


if __name__ == '__main__':
    main(sys.stdin)
