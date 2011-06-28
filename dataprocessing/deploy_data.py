#!/usr/bin/env python

import json
import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import config
import utils

if len(sys.argv) < 2:
    sys.exit('You must specify "staging" or "production" as an argument to this script.')

ENVIRONMENT = sys.argv[1]

collection = utils.get_geography_collection()

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

for geography in collection.find():
    row_count += 1

    del geography['_id']

    k = Key(bucket)
    k.key = '%s/%s.jsonp' % (geography['metadata']['STATE'], geography['geoid'])
    jsonp = 'geoid_%s(%s)' % (geography['geoid'], json.dumps(geography))
    compressed = utils.gzip_data(jsonp)

    k.set_contents_from_string(compressed, headers={ 'Content-encoding': 'gzip', 'Content-Type': 'application/javascript' }, policy='private')

    if row_count % 100 == 0:
        print ' Deployed %i...' % row_count

    deployed += 1

print '  Row count: %i' % row_count
print '  Deployed: %i' % deployed

