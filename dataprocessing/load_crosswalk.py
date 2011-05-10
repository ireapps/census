#!/usr/bin/env python

import sys

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config

if len(sys.argv) < 2:
    sys.exit('You must provide the filename of a CSV as an argument to this script.')

FILENAME = sys.argv[1]

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.GEOGRAPHIES_COLLECTION]

with open(FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    row_count = 0

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))
        
        geography = collection.find_one({ 'geoid': row_dict['GEOID10'] })

        if not geography:
            continue

        pop_pct_2000 = float(row_dict['POPPCT00']) / 100

        if 'xwalk' not in geography:
            geography['xwalk'] = {} 

        geography['xwalk'][row_dict['GEOID00']] = pop_pct_2000

        collection.save(geography) 
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

