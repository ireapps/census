#!/usr/bin/env python

import json

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pymongo import Connection

import config
import utils

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKET)

for geography in collection.find():
    row_count += 1

    del geography['_id']

    k = Key(bucket)
    k.key = '%s/%s.jsonp' % (geography['metadata']['STATE'], geography['geoid'])
    jsonp = 'geoid_%s(%s)' % (geography['geoid'], json.dumps(geography))
    compressed = utils.gzip_data(jsonp)

    k.set_contents_from_string(compressed, headers={ 'Content-encoding': 'gzip', 'Content-Type': 'application/javascript' }, policy='private')

    if row_count % 100 == 0:
        print 'Deployed %i...' % row_count

    deployed += 1

print 'Row count: %i' % row_count
print 'Deployed: %i' % deployed

