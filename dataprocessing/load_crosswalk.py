#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

connection = Connection()
db = connection['census']
collection = db['crosswalk']

inserts = 0
row_count = 0

with open('us2010trf.csv') as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        collection.insert(row_dict)
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts
