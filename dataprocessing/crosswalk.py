#!/usr/bin/env python

import sys

from pymongo import Connection, objectid

import config
import utils

if len(sys.argv) < 2:
    sys.exit('You must provide a state fips code as an argument to this script.')

STATE_FIPS = sys.argv[1]

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]
collection_2000 = db[config.GEOGRAPHIES_2000_COLLECTION]

row_count = 0
inserts = 0

for geography in collection.find({ 'metadata.STATE': STATE_FIPS }, fields=['data', 'geoid', 'metadata.NAME', 'sumlev', 'xwalk']):
    row_count += 1

    # TRACTS - require true crosswalk
    if geography['sumlev'] == config.SUMLEV_TRACT:
        geography_2000s = list(utils.find_geographies_for_xwalk(collection_2000, geography, fields=['data', 'geoid']))

        # Tract is new
        if not geography_2000s:
            continue

        data = {}

        for table in geography_2000s[0]['data']['2000']:
            data[table] = {}

            for k, v in geography_2000s[0]['data']['2000'][table].items():
                parts = []

                for g in geography_2000s:
                    value = float(g['data']['2000'][table][k])
                    pct = geography['xwalk'][g['geoid']]

                    parts.append(value * pct)

                data[table][k] = int(sum(parts))

        geography['data']['2000'] = data
    # OTHER SUMLEVS - can be directly compared by geoid
    else:
        geography_2000 = collection_2000.find_one({ 'geoid': geography['geoid'] }, fields=['data'])

        if not geography_2000:
            print 'Couldn\'t find matching 2000 geography for %s (%s)' % (geography['metadata']['NAME'], geography['geoid'])

            continue

        geography['data']['2000'] = geography_2000['data']['2000']

    collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'data': geography['data'] } }, safe=True)
    inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

