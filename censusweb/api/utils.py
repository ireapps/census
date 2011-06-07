#!/usr/bin/env python

import simplejson
import zlib

from django.conf import settings
import requests

def strip_callback(data):
    return data[data.index('(') + 1:-1]

def fetch_geography(geoid):
    url = '%s%s.jsonp' % (settings.API_URL, geoid)
    r = requests.get(url)
    content = strip_callback(zlib.decompress(r.content))
    return simplejson.loads(content)

def fetch_geographies(geoids):
    return [fetch_geography(geoid) for geoid in geoids]

def fetch_labels(dataset):
    url = '%s%s_labels.jsonp' % (settings.API_URL, dataset)
    r = requests.get(url)
    content = strip_callback(zlib.decompress(r.content))
    return simplejson.loads(content)
 
