#!/usr/bin/env python

import sys

from boto.s3.connection import S3Connection

import config

if len(sys.argv) < 3:
    sys.exit('You must "staging" or "production" and a state fips code as arguments to this script.')

ENVIRONMENT = sys.argv[1]
STATE_FIPS = sys.argv[2]

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

for i, k in enumerate(bucket.list('%s/' % STATE_FIPS)):
    k.make_public()
    
    if i % 100 == 0:
        print 'Processed %i...' % i

