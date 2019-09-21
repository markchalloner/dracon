#!/usr/bin/env python3
from datetime import datetime

import psycopg2
import logging

logger = logging.getLogger(__name__)

VULNERABILITIES = {
    'table_name': 'vulnerabilities',
    'fields': [
        {
            'name': 'target',
            'type': 'TEXT'
        },
        {
            'name': 'title',
            'type': 'TEXT'
        },
        {
            'name': 'severity',
            'type': 'INTEGER'
        },
        {
            'name': 'cvss',
            'type': 'FLOAT'
        },
        {
            'name': 'confidence',
            'type': 'INTEGER'
        },
        {
            'name': 'description',
            'type': 'TEXT'
        },
        {
            'name': 'hash',
            'type': 'TEXT',
            'unique': True
        },
        {
            'name': 'found_counter',
            'type': 'INTEGER'
        },

        {
            'name': 'first_seen',
            'type': 'TIMESTAMP'
        },
    ]
}

CHANGES = {
    'table_name': 'changes',
    'fields': [
        {
            'name': 'tester',
            'type': 'INTEGER',
        },
        {
            'name': 'vulnerability',
            'type': 'REFERENCES vulnerabilities(id)',
        },
        {
            'name': 'timestamp',
            'type': 'TIMESTAMP',
        },
        {
            'name': 'operation',
            'type': 'TEXT',
        },
        {
            'name': 'value',
            'type': 'BOOLEAN',
        },
    ]
}

TABLES = [VULNERABILITIES, CHANGES]


class DraconDBHelper:
    db_handler = None

    def connect(self, uri: str = "postgres://dracon:dracon@dracon-enrichment-db/dracondb"):
        """
            Connects the service to the Dracon db
        """
        self.db_handler = psycopg2.connect(uri
        )

    def generate_create_tables(self) -> list:
        """
            Transform the table definitions into SQL statements that when executed
            will create the tables with the appropriate format.

            :returns list of statements to execute
        """
        stmts = []

        for t_obj in TABLES:
            t_stmt = "CREATE TABLE " + t_obj['table_name'] + "("

            field_stmts = [
                'id SERIAL PRIMARY KEY'
            ]

            for f in t_obj['fields']:
                if (f['type'].startswith('REFERENCES')):
                    f_stmt = f"{f['name']} INTEGER, FOREIGN KEY({f['name']}) {f['type']}"
                else:
                    f_stmt = f"{f['name']} {f['type']}"

                    f_keys = f.keys()
                    if 'default' not in f_keys:
                        f_stmt += " NOT NULL"

                field_stmts.append(f_stmt)

            t_stmt += ', '.join(field_stmts) + ");"
            stmts.append(t_stmt)

        return stmts

    def truncate_tables(self):
        """
            Truncate all the tables via the TABLES global var
        """
        with self.db_handler.new_connection() as db:
            with db:
                for table in TABLES:
                    t_name = table['table_name']
                    db.execute(f'TRUNCATE TABLE {t_name} CASCADE')

    def execute(self, fmt_expr: str, values: list = []):
        """
            Execute an sql statement using the class db handler
        """
        with self.db_handler.new_connection() as db:
            with db:
                return db.execute(fmt_expr, values)

    def result_hash_exists(self, hash: str = None) -> bool:
        query = """SELECT 1 FROM vulnerabilities WHERE hash=%s"""
        result = self.execute(query, [hash])
        if len(result) > 0:
            return True
        return False

    def get_issue_by_hash(self, issue_hash: str = None) -> list:
        keys = list(map(lambda dict_field: dict_field["name"], VULNERABILITIES['fields']))
        query = """SELECT """ + ', '.join(keys) + """ FROM """ + VULNERABILITIES[
            'table_name'] + """ WHERE hash=%s LIMIT 1"""

        # the above is important, Postgresql seems to return table fields in it's own order
        # we need a certain order so that we can map it to the dictionary

        data = self.execute(query, [issue_hash])

        result = []
        for el in data:
            result = (dict(zip(keys, el)))
        return result

    def increase_count(self, issue_hash: str = None):
        query = """UPDATE """ + VULNERABILITIES[
            'table_name'] + """ SET found_counter=found_counter+1 WHERE hash=%s"""
        self.execute(query, [issue_hash])

    def insert_issue(self, target: str, title: str, severity: int, cvss: float, confidence: int,
                     description: str, hash: str, found_counter: int, first_seen: datetime):
        query = """INSERT INTO vulnerabilities(target,title, severity, cvss, confidence,\
        description, hash, found_counter,first_seen)\
         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        self.execute(query, [target, title, severity, cvss, confidence, description, hash,
                             found_counter, first_seen])

    def get_all_issues(self):
        query = """SELECT * FROM """ + VULNERABILITIES['table_name']
        return self.execute(query)
