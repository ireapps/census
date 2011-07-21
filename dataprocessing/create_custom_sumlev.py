#!/usr/bin/env python

"""
Aggregate geoids (usually of blocks) to a new summary level, such as for wards,
community areas, or whatever. Takes a CSV mapping existing census geoids to
new features ID as an input. Example:

    150030084051004,1
    150030101004058,1
    150030102013031,2

In this case the first two blocks would be rolled up to form a new feature
with a unique id of "1". The third block would be copied into a new feature
with a unique id of "2".

A name must also be provided for the new summary level, this will also be
prefixed to each new geoid in order to prevent namespace collisions with
existing census geographies. For example, if the new summary level had been
named "test" in the previous example, then the newly created geographies
would have had geoids of "test_1" and "test_2".

Example usage:

    python create_custom_sumlev.py mapping_2000.csv sumlev_name 2000
    python create_custom_sumlev.py mapping_2010.csv sumlev_name 2010
"""

import csv
import sys

import utils

if len(sys.argv) < 4:
    sys.exit('You must provide the filename of a CSV mapping census geoids to new unique feature ids and name for the new summary level and a year.')

FILENAME = sys.argv[1]
NEW_SUMLEV = sys.argv[2]
YEAR = sys.argv[3]

if YEAR == '2010':
    collection = utils.get_geography_collection()
elif YEAR == '2000':
    collection = utils.get_geography2000_collection()
else:
    sys.exit('Invalid year: "%s"' % YEAR)
    
# Destroy any previous aggregations for this summary level
collection.remove({ 'sumlev': NEW_SUMLEV }, safe=True)

def make_custom_geoid(sumlev, feature_id):
    """
    Generate a unique geoid for the given feature.
    """
    return '%s_%s' % (sumlev, feature_id)

count_allocated = 0
count_new_features = 0

mapping = csv.reader(open(FILENAME, 'rU'))

for row in mapping:
    geoid, feature_id = row

    new_geoid = make_custom_geoid(NEW_SUMLEV, feature_id)

    old_geography = collection.find_one({ 'geoid': geoid })
    new_geography = collection.find_one({ 'geoid': new_geoid })

    # Create an aggregating geography if it doesn't exist
    if not new_geography:
        new_geography = {
            'sumlev': NEW_SUMLEV,
            'geoid': new_geoid,
            'metadata': {
                'NAME': str(feature_id),
            },
            'data': {
                YEAR: {},
            }
        }

        count_new_features += 1
        
    # Update new geography with values from constituent block
    for table in old_geography['data'][YEAR]:
        if table not in new_geography['data'][YEAR]:
            new_geography['data'][YEAR][table] = {}

        for field, value in old_geography['data'][YEAR][table].items():
            if field not in new_geography['data'][YEAR][table]:
                new_geography['data'][YEAR][table][field] = 0

            new_geography['data'][YEAR][table][field] = float(new_geography['data'][YEAR][table][field]) + float(value)

    collection.save(new_geography, safe=True) 

    count_allocated += 1

print 'Allocated: %i' % count_allocated
print 'New Features: %i' % count_new_features

