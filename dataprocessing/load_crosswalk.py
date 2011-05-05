#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.CROSSWALK_COLLECTION]

with open(config.CROSSWALK_FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    row_count = 0

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        collection.insert(row_dict)
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

