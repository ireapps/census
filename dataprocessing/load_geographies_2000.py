#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config
import utils

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_2000_COLLECTION]

with open(config.GEOGRAPHIES_2000_FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    updates = 0
    row_count = 0

    for row in rows:
        row_count += 1

        geography = {
            #'sumlev': '',
            #'geoid': '',
            #'metadata': {},
            #'xrefs': [],
            #'data': {}
            #'xwalk': {}
            #'shape': ''     # TODO
        }
        row_dict = dict(zip(headers, row))

        if row_dict['SUMLEV'] not in config.SUMLEVS:
            continue

        geography['sumlev'] = row_dict.pop('SUMLEV')
        geography['geoid'] = utils.GEOID_COMPUTERS[geography['sumlev']](row_dict)

        xref = utils.xref_from_row_dict(row_dict) 

        existing = collection.find_one(geography)
        if existing:
            if xref not in existing['xrefs']:
                existing['xrefs'].append(xref)
                collection.save(existing)

                updates += 1

            continue

        geography['xrefs'] = [xref]
        geography['data'] = {}
        geography['metadata'] = row_dict

        collection.save(geography)
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts
print 'Updated: %i' % updates

