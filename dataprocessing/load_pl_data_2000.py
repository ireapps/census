#!/usr/bin/env python

import sys

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection, objectid

import config
import utils

if len(sys.argv) < 2:
    sys.exit('You must provide the filename of a CSV as an argument to this script.')

FILENAME = sys.argv[1]

YEAR = '2000'

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.GEOGRAPHIES_2000_COLLECTION]

with open(FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    updates = 0
    row_count = 0

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        xref = utils.xref_from_row_dict(row_dict)

        geography = utils.find_geography_by_xref(collection, xref, fields=['data']) 

        if not geography:
            continue

        if YEAR not in geography['data']:
            geography['data'][YEAR] = {}

        tables = {}

        for k, v in row_dict.items():
            t = k[0] + k[3]

            if t not in tables:
                tables[t] = {}

            tables[t][k] = int(v)

        for k, v in tables.items():
            geography['data'][YEAR][k] = v 

        collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'data': geography['data'] } }, safe=True)
        updates += 1

print 'Row count: %i' % row_count
print 'Updated: %i' % updates

