#!/usr/bin/env python

import argparse

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

def geoid_state(r):
    return r['STATE']

def geoid_county(r):
    return r['STATE'] + r['COUNTY']

def geoid_tract(r):
    return r['STATE'] + r['COUNTY'] + r['TRACT']

def geoid_place(r):
    return r['STATE'] + r['PLACE']

# TODO: Load all summary levels
GEOID_COMPUTERS = {
    #'000': geoid_nation,
    '040': geoid_state,
    '050': geoid_county,
    #'140': geoid_tract,
    #'160': geoid_place,
}

def load_geographies(filename):
    connection = Connection()
    db = connection['census']
    collection = db['geographies']

    with open('ilgeo2000.csv') as f:
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
                #'CHARITER': row_dict.pop('CHARITER'),
                #'CIFSN': row_dict.pop('CIFSN'),
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    load_geographies(args.filename)
