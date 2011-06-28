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

collection = utils.get_label_collection()

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

for dataset in collection.find():
    row_count += 1

    del dataset['_id']

    print dataset['dataset']

    k = Key(bucket)
    k.key = '%s_labels.jsonp' % dataset['dataset']
    jsonp = 'labels_%s(%s)' % (dataset['dataset'], json.dumps(dataset))
    compressed = utils.gzip_data(jsonp)

    k.set_contents_from_string(compressed, headers={ 'Content-encoding': 'gzip', 'Content-Type': 'application/json' }, policy='public-read')

    deployed += 1

print 'Row count: %i' % row_count
print 'Deployed: %i' % deployed

