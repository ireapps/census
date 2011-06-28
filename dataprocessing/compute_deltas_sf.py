#!/usr/bin/env python

from pymongo import objectid

import config
import utils

collection = utils.get_geography_collection()

row_count = 0
computations = 0

for geography in collection.find({}, fields=['data']):
    row_count += 1

    if 'delta' not in geography['data']:
        geography['data']['delta'] = {} 

    if 'pct_change' not in geography['data']:
        geography['data']['pct_change'] = {}

    # Skip geographies which did not have data in 2000 (e.g. newly established places)
    if '2000' not in geography['data']:
        continue

    for table in geography['data']['2010']:
        # Skip tables with no equivalent in 2000
        if table not in geography['data']['2000']:
            continue

        if table not in geography['data']['delta']:
            geography['data']['delta'][table] = {}
        
        if table not in geography['data']['pct_change']:
            geography['data']['pct_change'][table] = {}

        for k, v in geography['data']['2010'][table].items():
            if k not in geography['data']['2000'][table]:
                continue

            value_2010 = float(v)
            value_2000 = float(geography['data']['2000'][table][k])

            if value_2000 == 0:
                continue

            geography['data']['delta'][table][k] = str(value_2010 - value_2000)
            geography['data']['pct_change'][table][k] = str((value_2010 - value_2000) / value_2000)

    collection.update({ '_id': objectid.ObjectId(geography['_id']) }, { '$set': { 'data': geography['data'] } }, safe=True)
    computations += 1

print ' Row count: %i' % row_count
print ' Computations: %i' % computations


