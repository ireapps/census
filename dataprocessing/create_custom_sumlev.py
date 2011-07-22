#!/usr/bin/env python

"""
Script for generating custom summary levels:

Note: You must have already run batch_sf.sh before using this script. If you want
to aggregate blocks (the normal case), you'll need to have added SUMLEV_BLOCK to
SUMLEVS in config.py before running the batch.

Aggregate geoids (usually of blocks) to a custom summary level, such as wards,
community areas, or neighborhoods. Takes a CSV mapping existing census geoids to
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

Once this script has been run you can rerun the crosswalk and delta computation
scripts for only the new summary level:

    python crosswalk.py test
    python compute_deltas_sf.py test
"""

import csv
import sys

import utils

def make_custom_geoid(sumlev, feature_id):
    """
    Generate a unique geoid for the given feature.
    """
    return '%s_%s' % (sumlev, feature_id)

def create_custom_sumlev(collection, filename, new_sumlev, year):
    """
    Create a custom summary level by aggregating blocks
    according to a pre-generated mapping.
    """
    # Destroy any previous aggregations for this summary level
    collection.remove({ 'sumlev': new_sumlev }, safe=True)

    count_allocated = 0
    count_new_features = 0

    mapping = csv.reader(open(filename, 'rU'))

    for row in mapping:
        geoid, feature_id = row

        new_geoid = make_custom_geoid(new_sumlev, feature_id)

        old_geography = collection.find_one({ 'geoid': geoid })
        new_geography = collection.find_one({ 'geoid': new_geoid })

        # Create an aggregating geography if it doesn't exist
        if not new_geography:
            new_geography = {
                'sumlev': new_sumlev,
                'geoid': new_geoid,
                'metadata': {
                    'NAME': str(feature_id),
                },
                'data': {
                    year: {},
                }
            }

            count_new_features += 1
            
        # Update new geography with values from constituent block
        for table in old_geography['data'][year]:
            if table not in new_geography['data'][year]:
                new_geography['data'][year][table] = {}

            for field, value in old_geography['data'][year][table].items():
                if field not in new_geography['data'][year][table]:
                    new_geography['data'][year][table][field] = 0

                new_geography['data'][year][table][field] = float(new_geography['data'][year][table][field]) + float(value)

        collection.save(new_geography, safe=True) 

        count_allocated += 1

    print 'Allocated: %i' % count_allocated
    print 'New Features: %i' % count_new_features

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit('You must provide the filename of a CSV mapping census geoids to new unique feature ids and name for the new summary level and a year.')

    filename = sys.argv[1]
    new_sumlev = sys.argv[2]
    year = sys.argv[3]

    if year == '2010':
        collection = utils.get_geography_collection()
    elif year == '2000':
        collection = utils.get_geography2000_collection()
    else:
        sys.exit('Invalid year: "%s"' % year)

    create_custom_sumlev(collection, filename, new_sumlev, year)

