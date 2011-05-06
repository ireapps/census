#!/usr/bin/env python

from pymongo import Connection

import config
import utils

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

row_count = 0
computations = 0

for geography in collection.find():
    row_count += 1

    # TODO: do stuff

    collection.save(geography)
    computations += 1

print 'Row count: %i' % row_count
print 'Computations: %i' % computations


