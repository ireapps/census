#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

connection = Connection()
db = connection['census']
collection = db['geographies']

def geoid_state(r):
    return r['STATE']

GEOID_COMPUTERS = {
    '040': geoid_state,
}

inserts = 0
updates = 0
row_count = 0

with open('ilgeo2000.csv') as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    for row in rows:
        row_count += 1

        geography = {
            #'sumlev': '',
            #'geoid': '',
            #'metadata': {},
            #'xrefs': [],
            #'data': {}
            #'shape': ''     # TODO
        }
        row_dict = dict(zip(headers, row))

        if row_dict['SUMLEV'] not in GEOID_COMPUTERS:
            continue

        geography['sumlev'] = row_dict.pop('SUMLEV')
        geography['geoid'] = GEOID_COMPUTERS[geography['sumlev']](row_dict)

        xref = { 
            'FILEID': row_dict.pop('FILEID'),
            'STUSAB': row_dict.pop('STUSAB'),
            'CHARITER': row_dict.pop('CHARITER'),
            'CIFSN': row_dict.pop('CIFSN'),
            'LOGRECNO': row_dict.pop('LOGRECNO')
        }

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

