#!/usr/bin/env python

import sys

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config

if len(sys.argv) < 2:
    sys.exit('You must provide a state fips code and the filename of a CSV as an argument to this script.')

STATE_FIPS = sys.argv[1]
FILENAME = sys.argv[2]

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.GEOGRAPHIES_COLLECTION]

inserts = 0
row_count = 0

# Create dummy 2000->2010 crosswalk
if FILENAME == 'FAKE':
    for geography in collection.find({ 'metadata.STATE': STATE_FIPS }, fields=['xwalk']):
        if 'xwalk' not in geography:
            geography['xwalk'] = {} 

        geography['xwalk'][geography['geoid']] = 1.0

        collection.save(geography) 
        row_count += 1
        inserts += 1
else:
    with open(FILENAME) as f:
        rows = UnicodeCSVReader(f)
        headers = rows.next()

        for row in rows:
            row_count += 1
            row_dict = dict(zip(headers, row))

            if row_dict['STATE10'] != STATE_FIPS:
                continue
            
            geography = collection.find_one({ 'geoid': row_dict['GEOID10'] }, fields=['xwalk'])

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

