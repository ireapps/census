#!/usr/bin/env python

import json
import sys
import zlib

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pymongo import Connection

import config

STATE = sys.argv[1]
try: CLEAR = sys.argv[2]
except: CLEAR = None

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKET)

k = Key(bucket)
k.key = 'states.jsonp'

try:
    data = k.get_contents_as_string()
    states = json.loads(zlib.decompress(data))
except S3ResponseError:
    states = []

if CLEAR == 'CLEAR':
    states = [STATE]
else:
    states.append(STATE)

jsonp = 'states(%s)' % json.dumps(states)
k.set_contents_from_string(zlib.compress(jsonp), headers={ 'Content-encoding': 'deflate', 'Content-Type': 'application/json' }, policy='public-read')


