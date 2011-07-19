#!/usr/bin/env python

import sys

from csvkit.unicsv import UnicodeCSVReader
from pymongo import objectid

import config
import utils

if len(sys.argv) < 2:
    sys.exit('You must provide a state fips code and the filename of a CSV as an argument to this script.')

STATE_FIPS = sys.argv[1]
FILENAME = sys.argv[2]

collection = utils.get_geography_collection()

inserts = 0
row_count = 0

if config.SUMLEV_BLOCK not in config.SUMLEVS:
    print 'Skipping block crosswalk.'
    sys.exit()

with open(FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    for row in rows:
        row_count += 1
        row_dict = dict(zip(headers, row))

        geoid00 = ''.join([
            row_dict['STATE_2000'].rjust(2, '0'),
            row_dict['COUNTY_2000'].rjust(3, '0'),
            row_dict['TRACT_2000'].rjust(6, '0'),
            row_dict['BLK_2000'].rjust(4, '0')
            ])
        geoid10 = ''.join([
            row_dict['STATE_2010'].rjust(2, '0'),
            row_dict['COUNTY_2010'].rjust(3, '0'),
            row_dict['TRACT_2010'].rjust(6, '0'),
            row_dict['BLK_2010'].rjust(4, '0')
            ])

        geography = collection.find_one({ 'geoid': geoid10 }, fields=['xwalk'])

        if not geography:
            continue

        if row_dict['AREALAND_INT'] == '0':
            pct = 0
        else:
            pct = float(row_dict['AREALAND_INT']) / float(row_dict['AREALAND_2000'])

        #pop_pct_2000 = float(row_dict['POPPCT00']) / 100
        #house_pct_2000 = float(row_dict['HUPCT00']) / 100

        if 'xwalk' not in geography:
            geography['xwalk'] = {} 

        geography['xwalk'][geoid00] = {
            'POPPCT00': pct,
            'HUPCT00': pct
        }

        collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'xwalk': geography['xwalk'] } }, safe=True) 
        inserts += 1

print "State: %s" % STATE_FIPS
print "File: %s" % FILENAME
print ' Row count: %i' % row_count
print ' Inserted: %i' % inserts

