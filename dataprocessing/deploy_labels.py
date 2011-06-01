#!/usr/bin/env python

import json
import zlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pymongo import Connection

import config

connection = Connection()
db = connection[config.LABELS_DB]
collection = db[config.LABELS_COLLECTION]

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKET)

for dataset in collection.find():
    row_count += 1

    del dataset['_id']

    k = Key(bucket)
    k.key = '%s_labels.jsonp' % dataset['dataset']
    jsonp = 'labels_%s(%s)' % (dataset['dataset'], json.dumps(dataset))
    k.set_contents_from_string(zlib.compress(jsonp), headers={ 'Content-encoding': 'deflate', 'Content-Type': 'application/json' }, policy='public-read')

    deployed += 1

print 'Row count: %i' % row_count
print 'Deployed: %i' % deployed

