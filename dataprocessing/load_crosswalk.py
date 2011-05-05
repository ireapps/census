#!/usr/bin/env python

import argparse

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

def load_crosswalk(filename):
    connection = Connection()
    db = connection['census']
    collection = db['crosswalk']

    with open(filename) as f:
        rows = UnicodeCSVReader(f)
        headers = rows.next()

        inserts = 0
        row_count = 0

        for row in rows:
            row_count += 1
            row_dict = dict(zip(headers, row))

            collection.insert(row_dict)
            inserts += 1

    print 'Row count: %i' % row_count
    print 'Inserted: %i' % inserts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    load_crosswalk(args.filename)
