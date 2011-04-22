#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

connection = Connection()
db = connection['census']
collection = db['geographies']

inserts = 0
row_count = 0

with open('il000012000.csv') as f:
    year = 2000
    table = 'PL1'

    rows = UnicodeCSVReader(f)
    headers = rows.next()

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        xref = { 
            'FILEID': row_dict.pop('FILEID'),
            'STUSAB': row_dict.pop('STUSAB'),
            'CHARITER': row_dict.pop('CHARITER'),
            'CIFSN': row_dict.pop('CIFSN'),
            'LOGRECNO': row_dict.pop('LOGRECNO')
        }

        TKTK = """
        db.geographies.find({ 
            "xrefs": {
                "$elemMatch": { 
                    "FILEID": "uPL",
                    "STUSAB": "IL",
                    "CHARITER": "000",
                    "CIFSN": "",
                    "LOGRECNO": "0000001" }}})
        """

        geography = collection.find_one(
            '{ "xrefs": { "$elemMatch": %s } }' % xref)

        if not geography:
            print 'Unable to find geography for %s' % xref
            continue

        if year not in geography['data']:
            geography['data'][year] = {}

        geography['data'][year][table] = row_dict

        collection.save(geography)
        inserts += 1

        print 'Inserted xref!'

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

