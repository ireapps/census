#!/usr/bin/env python

import json
import sys

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from boto.s3.key import Key

import config
import utils

def update_state_list(environment, state, clear=False, remove=False):
    c = S3Connection()
    bucket = c.get_bucket(config.S3_BUCKETS[environment])

    k = Key(bucket)
    k.key = 'states.jsonp'

    try:
        data = k.get_contents_as_string()

        # No existing file 
        if not data:
            raise S3ResponseError()
        
        # Strip off jsonp wrapper
        contents = utils.gunzip_data(data)
        data = contents[7:-1]

        states = json.loads(data)
    except S3ResponseError:
        states = []
    if remove:
        states.remove(state)
        print 'Removed %s from list of available states' % state
    elif clear:
        states = [state]
        print 'Reset list of available states and added %s' % state
    else:
        if state not in states:
            states.append(state)

            print '%s added to available state list' % state
        else:
            print '%s is already available' % state
    
    states.sort()
    jsonp = 'states(%s)' % json.dumps(states)
    compressed = utils.gzip_data(jsonp)

    k.set_contents_from_string(compressed, headers={ 'Content-encoding': 'gzip', 'Content-Type': 'application/json' }, policy='public-read')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('You must specify either "staging" or "production" and a state as arguments to this script.')

    ENVIRONMENT = sys.argv[1]
    STATE = sys.argv[2]
    try:
        OPERATION = sys.argv[3]
    except:
        OPERATION = None

    update_state_list(ENVIRONMENT, STATE, (OPERATION == 'CLEAR'), (OPERATION == 'REMOVE'))
