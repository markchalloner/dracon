import sys

from elasticsearch import Elasticsearch

import certifi
from consumers.consumer import Consumer
import logging
import argparse
from gen import engine_pb2

from utils.file_utils import load_files

logger = logging.getLogger(__name__)


class ES_Client:

    def __init__(self, ca: str='', url: str = '', dry_run: bool = None):

        url = url
        ca = ca
        if not url:
            raise ValueError('Must set elasticsearch_url')
        self.es = Elasticsearch([url], ca_certs=ca, timeout=120)
        self.dry_run = dry_run

    def send(self, index: str, doc_type: str, data: dict):
        """Submit some data to Elasticsearch.

        :param index str: Elasticsearch index to send to
        :param doc_type str: Elasticsearch document type
        :param data dict: Arbitrary dict of data to send to Elasticsearch.
        """
        if self.dry_run:
            print('Elasticsearch send: index=%s doc_type=%s data=%s',
                  index, doc_type, data)
            return
        res = self.es.index(index=index, doc_type=doc_type, body=data)
        if not (res.get('created') or res.get('result') == 'created'):
            raise Exception(
                'Failed to submit to Elasticsearch: created:{} result:{}'.format(
                    res.get('created'), res.get('result')
                )
            )


class ElasticsearchConsumer(Consumer):

    def __init__(self, config: object):
        self.dry_run = config.dry_run
        self.index = config.es_index
        self.es_location = config.es_url
        self.pvc_location = config.pvc_location
        self.raw = config.raw

        if ((self.index is None) or (self.es_location is None)):
            raise AttributeError("Elasticsearch config is incomplete")
        if (self.pvc_location is None):
            raise AttributeError("PVC claim location is missing")

    def _load_enriched_results(self):
        """Load a set of LaunchToolResponse protobufs into a list for processing"""
        return super().load_results()

    def load_results(self) -> list:
        if not self.raw:
            print('Handling enriched results only')
            return self._load_enriched_results(), False
        else:
            print('Handling raw results only')
            return self._load_plain_results(), True

    def _load_plain_results(self):
        scan_results = engine_pb2.LaunchToolResponse()
        return load_files(scan_results, self.pvc_location)

    def _load_enriched_results(self):
        """Load a set of LaunchToolResponse protobufs into a list for processing"""
        return super().load_results()

    def send_results(self, collected_results: list):
        """
        Take a list of LaunchToolResponse protobufs and sends them to Elasticsearch

        :param collected_results: list of LaunchToolResponse protobufs
        """

        if 'https' in self.es_location:
            es_client = ES_Client(
                url=self.es_location, ca=certifi.where(), dry_run=self.dry_run)
        else:
            es_client = ES_Client(
                url=self.es_location, ca=None, dry_run=self.dry_run)
        if (self.dry_run):
            print(
                'dry_run set: not sending data to ElasticSearch instance')
    
        for sc in collected_results:
            for el in sc:
                for iss in el.issues:
                    if self.raw:
                        scan = sc
                        issue = iss
                        first_found = scan.scan_info.scan_start_time.ToJsonString()
                        false_positive = False
                    else:
                        #from pprint import pprint
                        #pprint(iss)

                        issue = iss.raw_issue
                        first_found = iss.first_seen.ToJsonString()
                        false_positive = iss.false_positive
                        scan = el.original_results

                    data = {
                        'scan_start_time': scan.scan_info.scan_start_time.ToJsonString(),
                        'scan_id': scan.scan_info.scan_uuid,
                        'tool_name': scan.tool_name,
                        'target': issue.target,
                        'type': issue.type,
                        'title': issue.title,
                        'severity': issue.severity,
                        'cvss': issue.cvss,
                        'confidence': issue.confidence,
                        'description': issue.description,
                        'first_found': first_found,
                        'false_positive': false_positive
                    }
                    print('sending to elasticsearch')
                    es_client.send(index=self.index,doc_type=scan.tool_name, data=data)


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
        parser.add_argument(
            '--raw', default=False, action="store_true", help=('if set will only parse raw results,'
                                                               'otherwirse only enriched results will be parsed'))
        args = parser.parse_args()
        ec = ElasticsearchConsumer(args)
    except AttributeError as e:
        logger.error('A required argument is missing: ' + str(e))
        raise
    try:
        print('Loading results from the PVC at ' + str(ec.pvc_location))
        collected_results = ec.load_results()
    except SyntaxError as e:
        logger.error('Unable to load results from the PVC: ' + str(e))
        raise
    try:
        print('Sending results to Elasticsearch: %s index %s ' %
              (args.es_url, args.es_index))
        ec.send_results(collected_results)
    except Exception as e:
        logger.error('Unable to send results to Elasticsearch:' + str(e))
        raise
    print('Done!')


if __name__ == '__main__':
    main()
