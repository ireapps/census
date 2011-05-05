#!/usr/bin/env python

import argparse

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

def load_data(filename, year, table):
    connection = Connection()
    db = connection['census']
    collection = db['geographies']

    with open(filename) as f:
        rows = UnicodeCSVReader(f)
        headers = rows.next()

        inserts = 0
        row_count = 0

        for row in rows:
            row_count += 1
            row_dict = dict(zip(headers, row))

            xref = { 
                'FILEID': row_dict.pop('FILEID'),
                'STUSAB': row_dict.pop('STUSAB'),
                #'CHARITER': row_dict.pop('CHARITER'),
                #'CIFSN': row_dict.pop('CIFSN'),
                'LOGRECNO': row_dict.pop('LOGRECNO')
            }

            geography = collection.find_one(
                { "xrefs": { "$elemMatch": xref } })

            if not geography:
                continue

            if year not in geography['data']:
                geography['data'][year] = {}

            geography['data'][year][table] = row_dict

            collection.save(geography)
            inserts += 1

    print 'Row count: %i' % row_count
    print 'Inserted: %i' % inserts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('year')
    parser.add_argument('table')
    args = parser.parse_args()

    load_data(args.filename, args.year, args.table)

