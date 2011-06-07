#!/usr/bin/env python

import csv

from pymongo import Connection, objectid

import config
import utils

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

# Maps 2010 field names to their 2000 equivalents
KEY_MAPPINGS = {}

with open('field_mappings_2000_2010.csv', 'rU') as f:
    reader = csv.DictReader(f)

    for row in reader:
        # Skip fields that don't map
        if not row['field_2000']:
            continue

        if not row['field_2010']:
            continue

        # TODO - skipping computed fields
        if '-' in row['field_2000'] or '+' in row['field_2000']:
            continue

        if '-' in row['field_2010'] or '+' in row['field_2010']:
            continue

        KEY_MAPPINGS[row['field_2010']] = row['field_2000']

row_count = 0
computations = 0

for geography in collection.find({}, fields=['data']):
    row_count += 1

    if 'delta' not in geography['data']:
        geography['data']['delta'] = {} 

    if 'pct_change' not in geography['data']:
        geography['data']['pct_change'] = {}

    # Skip geographies which did not have data in 2000 (e.g. newly established places)
    if '2000' not in geography['data']:
        continue

    for table in geography['data']['2010']:
        if table not in geography['data']['delta']:
            geography['data']['delta'][table] = {}
        
        if table not in geography['data']['pct_change']:
            geography['data']['pct_change'][table] = {}

        for k, v in geography['data']['2010'][table].items():
            # TODO - Skip fields which don't exist in 2010 (because we're testing w/ 2000 data)
            if k not in KEY_MAPPINGS:
                continue

            # Skip fields which didn't have equivalents in 2000
            if not KEY_MAPPINGS[k]:
                continue

            key_2000 = KEY_MAPPINGS[k]
            table_2000 = utils.parse_table_from_key(key_2000)

            # TODO - 2000 data does not exist - happens when testing with 2010 data
            if table_2000 not in geography['data']['2000']:
                continue

            if key_2000 not in geography['data']['2000'][table_2000]:
                continue

            value_2010 = float(v)
            value_2000 = float(geography['data']['2000'][table_2000][key_2000])

            if value_2000 == 0:
                continue

            geography['data']['delta'][table][k] = str(value_2010 - value_2000)
            geography['data']['pct_change'][table][k] = str((value_2010 - value_2000) / value_2000)

    collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'data': geography['data'] } }, safe=True)
    computations += 1

print 'Row count: %i' % row_count
print 'Computations: %i' % computations


