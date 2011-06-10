#!/usr/bin/env python

import sys

from boto.s3.connection import S3Connection

import config
import get_state_fips
import update_state_list

if len(sys.argv) < 3:
    sys.exit('You must "staging" or "production" and a state name as arguments to this script.')

ENVIRONMENT = sys.argv[1]
STATE = sys.argv[2]
STATE_FIPS = get_state_fips.STATE_FIPS[STATE]

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

for i, k in enumerate(bucket.list('%s/' % STATE_FIPS)):
    k.make_public()
    
    if i % 100 == 0:
        print 'Processed %i...' % i

# Update available states list 
update_state_list.update_state_list(ENVIRONMENT, STATE)
