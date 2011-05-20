#!/usr/bin/env python

import sys

from pymongo import Connection

import config

if len(sys.argv) < 2:
    sys.exit('You must provide a state fips code as an argument to this script.')

STATE_FIPS = sys.argv[1]

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

row_count = 0
computations = 0

for geography in collection.find({ 'metadata.STATE': STATE_FIPS }):
    row_count += 1

    if 'delta' not in geography['data']:
        geography['data']['delta'] = {} 

    if 'pct_change' not in geography['data']:
        geography['data']['pct_change'] = {}

    # Skip geographies which did not have data in 2000 (e.g. newly established places)
    if '2000' not in geography['data']:
        continue

    for table in geography['data']['2010']:
        # Skip tables not in both years
        if table not in geography['data']['2000']:
            continue

        if table not in geography['data']['delta']:
            geography['data']['delta'][table] = {}
        
        if table not in geography['data']['pct_change']:
            geography['data']['pct_change'][table] = {}

        for k, v in geography['data']['2010'][table].items():
            # Skip data not in both tables (added since 2000)
            if k not in geography['data']['2000'][table]:
                continue

            value_2010 = v
            value_2000 = geography['data']['2000'][table][k]

            if value_2000 == 0:
                continue

            geography['data']['delta'][table][k] = value_2010 - value_2000
            geography['data']['pct_change'][table][k] = float(value_2010 - value_2000) / value_2000

    collection.save(geography)
    computations += 1

print 'Row count: %i' % row_count
print 'Computations: %i' % computations


