#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.GEOGRAPHIES_COLLECTION]

with open(config.CROSSWALK_FILENAME) as f:
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

        # TODO: this algorithm sourced from notes at:
        # http://lists.reporter.org/IRE/lists/CENSUS-L/2011-02/msg00057.html
        # BUT NOT TESTED!
        pop_pct_2000 = float(row_dict['POPPCT00'])

        if pop_pct_2000 == 0:
            continue

        if 'xwalk' not in geography:
            geography['xwalk'] = {} 
        else:
            print row_dict['GEOID10']

        geography['xwalk'][row_dict['GEOID00']] = pop_pct_2000

        collection.save(geography) 
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

