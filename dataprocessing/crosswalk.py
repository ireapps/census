#!/usr/bin/env python

import csv
import sys

from pymongo import objectid

import config
import utils

collection = utils.get_geography_collection()
collection_2000 = utils.get_geography2000_collection()

row_count = 0
inserts = 0

KEY_MAPPINGS = {}
CROSSWALK_FIELDS_BY_TABLE = {}

# Maps 2010 field names to their 2000 equivalents
with open('field_mappings_2000_2010.csv', 'rU') as f:
    reader = csv.DictReader(f)

    for row in reader:
        # Skip fields that don't map
        if not row['field_2000'].strip():
            continue

        if not row['field_2010'].strip():
            continue

        # TODO - skipping computed fields
        if '-' in row['field_2000'] or '+' in row['field_2000']:
            continue

        if '-' in row['field_2010'] or '+' in row['field_2010']:
            continue

        # Fields in 2000 may map to multiple fields in 2010 (e.g. P001001 -> P001001 and P004001)
        if row['field_2000'] not in KEY_MAPPINGS:
            KEY_MAPPINGS[row['field_2000']] = []

        KEY_MAPPINGS[row['field_2000']].append(row['field_2010'])

# Load crosswalk lookup table
with open('sf_crosswalk_key.csv') as f:
    reader = csv.reader(f)

    for row in reader:
        CROSSWALK_FIELDS_BY_TABLE[row[0]] = row[1]

for geography in collection.find({}, fields=['data', 'geoid', 'metadata.NAME', 'sumlev', 'xwalk']):
    row_count += 1
    
    data = {}

    # TRACTS & BLOCKS - require true crosswalk
    if geography['sumlev'] in [config.SUMLEV_TRACT, config.SUMLEV_BLOCK]:
        geography_2000s = list(utils.find_geographies_for_xwalk(collection_2000, geography, fields=['data', 'geoid']))

        print geography['geoid']

        # Tract is new
        if not geography_2000s:
            continue

        for table in geography_2000s[0]['data']['2000']:
            crosswalk_field = CROSSWALK_FIELDS_BY_TABLE[table]

            # Table contains medians or other values that can't be crosswalked
            if not crosswalk_field:
                continue

            for k, v in geography_2000s[0]['data']['2000'][table].items():
                try:
                    keys_2010 = KEY_MAPPINGS[k]
                except KeyError:
                    # Skip 2000 fields that don't exist in 2010
                    continue

                # Skip 2000 fields that don't have an equivalent in 2010
                if not keys_2010:
                    continue

                # Copy value to all 2010 fields which are comparable to this field in 2000
                for key_2010 in keys_2010:
                    table_2010 = utils.parse_table_from_key(key_2010)

                    if table_2010 not in data:
                        data[table_2010] = {}

                    parts = []

                    for g in geography_2000s:
                        value = float(g['data']['2000'][table][k])
                        pct = geography['xwalk'][g['geoid']][crosswalk_field]

                        parts.append(value * pct)

                    data[table_2010][key_2010] = int(sum(parts))

    # OTHER SUMLEVS - can be directly compared by geoid
    else:
        geography_2000 = collection_2000.find_one({ 'geoid': geography['geoid'] }, fields=['data'])

        if not geography_2000:
            print 'Couldn\'t find matching 2000 geography for %s (%s)' % (geography['metadata']['NAME'].encode('utf-8'), geography['geoid'])

            continue

        for table in geography_2000['data']['2000']:
            for k, v in geography_2000['data']['2000'][table].items():
                try:
                    keys_2010 = KEY_MAPPINGS[k]
                except KeyError:
                    # Skip 2000 fields that don't exist in 2010
                    continue

                # Skip 2000 fields that don't have an equivalent in 2010
                if not keys_2010:
                    continue

                # Copy value to all 2010 fields which are comparable to this field in 2000
                for key_2010 in keys_2010:
                    table_2010 = utils.parse_table_from_key(key_2010)

                    if table_2010 not in data:
                        data[table_2010] = {}

                    parts = []

                    data[table_2010][key_2010] = geography_2000['data']['2000'][table][k] 

    geography['data']['2000'] = data

    collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'data': geography['data'] } }, safe=True)
    inserts += 1

print ' Row count: %i' % row_count
print ' Inserted: %i' % inserts

