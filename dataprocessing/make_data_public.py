#!/usr/bin/env python

import sys

from boto.s3.connection import S3Connection

import config

if len(sys.argv) < 2:
    sys.exit('You must provide a state fips code as an argument to this script.')

STATE_FIPS = sys.argv[1]

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKET)

for k in bucket.list('%s/' % STATE_FIPS):
    k.make_public()

