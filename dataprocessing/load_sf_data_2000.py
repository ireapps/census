#!/usr/bin/env python

import re
import sys

from csvkit.unicsv import UnicodeCSVReader
from pymongo import objectid

import config
import utils

if len(sys.argv) < 2:
    sys.exit('You must provide the filename of a CSV as an argument to this script.')

FILENAME = sys.argv[1]

YEAR = '2000'

collection = utils.get_geography2000_collection()

with open(FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    updates = 0
    row_count = 0

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        xref = utils.xref_from_row_dict(row_dict)

        geography = utils.find_geography_by_xref(collection, xref) 
        if not geography:
            continue

        if YEAR not in geography['data']:
            geography['data'][YEAR] = {}

        tables = {}

        for k, v in row_dict.items():
            # Format table names to match labels
            t = utils.parse_table_from_key(k) 

            if t not in tables:
                tables[t] = {}

            tables[t][k] = v

        for k, v in tables.items():
            geography['data'][YEAR][k] = v 

        collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'data': geography['data'] } }, safe=True)
        updates += 1

print 'Row count: %i' % row_count
print 'Updated: %i' % updates

