import sys

import elasticsearch
import certifi
from consumers.consumer import Consumer
import logging
import argparse
logger = logging.getLogger(__name__)


class ElasticsearchConsumer(Consumer):

    def __init__(self, config: object):
        self.dry_run = config.dry_run
        self.index = config.es_index
        self.es_location = config.es_url
        self.pvc_location = config.pvc_location

        if ((self.index is None) or (self.es_location is None)):
            raise AttributeError("Elasticsearch config is incomplete")
        if (self.pvc_location is None):
            raise AttributeError("PVC claim location is missing")

    def load_results(self):
        """Load a set of LaunchToolResponse protobufs into a list for processing"""

        return super().load_results()

    def send_results(self, collected_results: list):
        """
        Take a list of LaunchToolResponse protobufs and sends them to Elasticsearch

        :param collected_results: list of LaunchToolResponse protobufs
        """

        es_client = elasticsearch.Client(
            self.es_location, certifi.where(), self.dry_run)

        if (self.dry_run):
            logger.info(
                'dry_run set: not sending data to ElasticSearch instance')

        for scan in collected_results:
            raw_scan = scan.original_results
            for issue in raw_scan.issues:
                es_client.send(
                    index=self.index,
                    doc_type=raw_scan.tool_name,
                    data={
                        'scan_start_time': raw_scan.scan_info.scan_start_time.ToJsonString(),
                        'scan_id': raw_scan.scan_info.scan_uuid,
                        'tool_name': raw_scan.tool_name,
                        'target': issue.target,
                        'type': issue.type,
                        'title': issue.title,
                        'severity': issue.severity,
                        'cvss': issue.cvss,
                        'confidence': issue.confidence,
                        'description': issue.description,
                    }
                )


def main():
    try:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '--dry_run', action='store_true', help='If set, will not upload any data to Elasticsearch')
        parser.add_argument(
            '--es_url', help='The Elasticsearch instance to send the scan results to')
        parser.add_argument(
            '--es_index', help='The Elasticsearch index to use')
        parser.add_argument(
            '--pvc_location', help='The location of the scan results')
        args = parser.parse_args()
        ec = ElasticsearchConsumer(args)
    except AttributeError as e:
        logger.error('A required argument is missing: ' + str(e))
        sys.exit(-1)
    try:
        logger.info('Loading results from the PVC at ' + str(ec.pvc_location))
        collected_results = ec.load_results()
    except SyntaxError as e:
        logger.error('Unable to load results from the PVC: ' + str(e))
        sys.exit(-1)
    try:
        logger.info('Sending results to Elasticsearch')
        ec.send_results(collected_results)
    except Exception as e:
        logger.error('Unable to send results to Elasticsearch:' + str(e))
        sys.exit(-1)
    logger.info('Done!')


if __name__ == '__main__':
    main()
