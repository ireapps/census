#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.GEOGRAPHIES_2000_COLLECTION]

with open(config.CROSSWALK_FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    row_count = 0

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))
        
        geography = collection.find_one({ 'geoid': row_dict['GEOID10'] })

        # TODO: this algorithm sourced from
        # http://lists.reporter.org/IRE/lists/CENSUS-L/2011-02/msg00057.html
        # BUT NOT TESTED!
        pct_land_2010 = float(row_dict['AREALANDPCT10PT'])
        total_land_2010 = float(row_dict['AREALAND10'])
        total_land_2000 = float(row_dict['AREALAND00'])

        if total_land_2000 == 0:
            pct_to_include = 1.0
        else:
            pct_to_include = (pct_land_2010 * total_land_2010) / total_land_2000

        if not geography:
            continue

        if 'xwalk' not in geography:
            geography['xwalk'] = []

        geography['xwalk'].append({
            'geoid10': row_dict['GEOID10'],
            'pct': pct_to_include
            })

        geography.save() 
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

