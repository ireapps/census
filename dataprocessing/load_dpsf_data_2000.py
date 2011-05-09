#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config
import utils

YEAR = '2000'

connection = Connection()
db = connection[config.CENSUS_DB] 
collection = db[config.GEOGRAPHIES_COLLECTION]

with open(config.DPSF_2000_DATA_FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    row_count = 0

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        if row_dict['SUMLEV'] not in utils.GEOID_COMPUTERS:
            continue

        geoid = utils.GEOID_COMPUTERS[row_dict['SUMLEV']](row_dict)

        geography = collection.find_one({ 'geoid': geoid }) 

        if not geography:
            continue

        if YEAR not in geography['data']:
            geography['data'][YEAR] = {}

        tables = {'DP1': {}}

        for k in ['RECTYP','SUMLEV','GEOCOMP','STATE','COUNTY','COUSUB','PLACE','CONCIT','MSACMSA','PMSA','AIANHH','ANRC','CD106','FUNCSTAT','AREANAME']:
            row_dict.pop(k)

        for k, v in row_dict.items():
            try:
                tables['DP1'][k] = int(v)
            except ValueError:
                tables['DP1'][k] = float(v)

        for k, v in tables.items():
            geography['data'][YEAR][k] = v 

        collection.save(geography)
        inserts += 1

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts


