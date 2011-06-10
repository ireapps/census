#!/usr/bin/env python

from StringIO import StringIO
import gzip
import json

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

    print dataset['dataset']

    k = Key(bucket)
    k.key = '%s_labels.jsonp' % dataset['dataset']
    jsonp = 'labels_%s(%s)' % (dataset['dataset'], json.dumps(dataset))

    s = StringIO()
    gz = gzip.GzipFile(fileobj=s, mode='wb')
    gz.write(jsonp)
    gz.close()

    k.set_contents_from_string(s.getvalue(), headers={ 'Content-encoding': 'gzip', 'Content-Type': 'application/json' }, policy='public-read')

    s.close()

    deployed += 1

print 'Row count: %i' % row_count
print 'Deployed: %i' % deployed

