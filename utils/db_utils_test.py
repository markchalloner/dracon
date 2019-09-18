#!/usr/bin/env python3
import hashlib
from datetime import datetime

import infrastructure.security.dracon.utils.db_utils as db
from infrastructure.security.dracon.tests import util_test
from vault.common.python.test_database import TestDatabase

from unittest import TestCase


class DraconDBHelperTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pg = TestDatabase().start()
        cls.helper = db.DraconDBHelper()
        cls.helper.connect(cls.pg.db_url)

        for s in cls.helper.generate_create_tables():
            cls.helper.execute(s)

    @classmethod
    def tearDownClass(cls):
        cls.pg.stop()

    def tearDown(self):
        self.helper.truncate_tables()

    def __add_dummy_vulnerability(self):
        md = hashlib.md5()
        md.update("Nobody inspects the spammish repetition".encode('utf-8'))
        test_hash = str(md.hexdigest())
        test_target = util_test.get_random_str(10)
        test_title = util_test.get_random_str(10)
        test_severity = 1
        test_cvss = 1.1
        test_confidence = 2
        test_description = util_test.get_random_str(10)
        test_hash = test_hash
        test_count = 3
        test_first_seen = datetime.utcnow()
        self.helper.insert_issue(target=test_target,
                                 title=test_title,
                                 severity=test_severity,
                                 cvss=test_cvss,
                                 confidence=test_confidence,
                                 description=test_description,
                                 hash=test_hash,
                                 found_counter=test_count,
                                 first_seen=test_first_seen)
        return {"target": test_target,
                "title": test_title,
                "severity": test_severity,
                "cvss": test_cvss,
                "confidence": test_confidence,
                "description": test_description,
                "hash": test_hash,
                "found_counter": test_count,
                "first_seen": test_first_seen}

    def test_generate_create_tables(self):
        stmts = [
            ("CREATE TABLE vulnerabilities(id SERIAL PRIMARY KEY, target TEXT NOT NULL, title TEXT"
             " NOT NULL, severity INTEGER NOT NULL, cvss FLOAT NOT NULL, confidence INTEGER NOT"
             " NULL, description TEXT NOT NULL, hash TEXT NOT NULL, found_counter INTEGER NOT"
             " NULL, first_seen TIMESTAMP NOT NULL);"),
            ("CREATE TABLE changes(id SERIAL PRIMARY KEY, tester INTEGER NOT NULL, vulnerability"
             " INTEGER, FOREIGN KEY(vulnerability) REFERENCES vulnerabilities(id),"
             " timestamp TIMESTAMP NOT NULL, operation TEXT NOT NULL, value BOOLEAN NOT NULL);")
            # noqa
        ]
        for s in self.helper.generate_create_tables():
            self.assertIn(s, stmts)

    def test_execute(self):
        self.assertNotEqual(self.helper.execute("SELECT * FROM VULNERABILITIES;"), False)

    def test_truncate_tables(self):
        self.helper.truncate_tables()

    def test_insert_issue(self):
        md = hashlib.md5()
        md.update("Nobody inspects the spammish repetition".encode('utf-8'))
        test_hash = str(md.hexdigest())
        test_target = util_test.get_random_str(10)
        test_title = util_test.get_random_str(10)
        test_severity = 1
        test_cvss = 1.1
        test_confidence = 2
        test_description = util_test.get_random_str(10)
        test_hash = test_hash
        test_count = 3
        test_first_seen = datetime.utcnow()
        self.helper.insert_issue(target=test_target,
                                 title=test_title,
                                 severity=test_severity,
                                 cvss=test_cvss,
                                 confidence=test_confidence,
                                 description=test_description,
                                 hash=test_hash,
                                 found_counter=test_count,
                                 first_seen=test_first_seen)
        issue = self.helper.get_issue_by_hash(test_hash)

        self.assertEqual(issue['target'], test_target)
        self.assertEqual(issue['title'], test_title)
        self.assertEqual(issue['severity'], test_severity)
        self.assertEqual(issue['cvss'], test_cvss)
        self.assertEqual(issue['confidence'], test_confidence)
        self.assertEqual(issue['description'], test_description)
        self.assertEqual(issue['hash'], test_hash)
        self.assertEqual(issue['found_counter'], test_count)
        self.assertEqual(issue['first_seen'], test_first_seen)

    def test_result_hash_exists(self):
        test_hash = self.__add_dummy_vulnerability()['hash']
        self.assertTrue(self.helper.result_hash_exists(test_hash))
        self.assertFalse(self.helper.result_hash_exists(util_test.get_random_str(10)))

    def test_get_issue_by_hash(self):
        test_issue = self.__add_dummy_vulnerability()
        issue = self.helper.get_issue_by_hash(test_issue['hash'])

        self.assertEqual(issue['target'], test_issue['target'])
        self.assertEqual(issue['title'], test_issue['title'])
        self.assertEqual(issue['severity'], test_issue['severity'])
        self.assertEqual(issue['cvss'], test_issue['cvss'])
        self.assertEqual(issue['confidence'], test_issue['confidence'])
        self.assertEqual(issue['description'], test_issue['description'])
        self.assertEqual(issue['hash'], test_issue['hash'])
        self.assertEqual(issue['found_counter'], test_issue['found_counter'])
        self.assertEqual(issue['first_seen'], test_issue['first_seen'])

        issue = self.helper.get_issue_by_hash(util_test.get_random_str(10))
        self.assertEqual(len(issue), 0)
        self.assertEqual(type(issue), list)

    def test_increase_count(self):
        test_issue = self.__add_dummy_vulnerability()
        test_hash = test_issue['hash']
        self.helper.increase_count(test_hash)
        issue = self.helper.get_issue_by_hash(test_hash)
        self.assertEqual(issue['found_counter'], test_issue['found_counter'] + 1)
