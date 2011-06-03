#!/usr/bin/env python

import simplejson
import zlib

import requests

def fetch_geography(geoid):
    url = 'http://s3.amazonaws.com/census-test/%s.json' % geoid
    r = requests.get(url)
    content = zlib.decompress(r.content)
    return simplejson.loads(content)

def fetch_geographies(geoids):
    return [fetch_geography(geoid) for geoid in geoids]

