#!/usr/bin/env python

import json
import zlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pymongo import Connection

import config

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
    k.key = '%(geoid)s.json' % geography
    k.set_contents_from_string(zlib.compress(json.dumps(geography)))

    deployed += 1

print 'Row count: %i' % row_count
print 'Deployed: %i' % deployed
