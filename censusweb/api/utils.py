#!/usr/bin/env python

import simplejson

from django.conf import settings
import requests

def strip_callback(data):
    return data[data.index('(') + 1:-1]

def _api_fetch(url):
    r = requests.get(url)
    content = strip_callback(r.content)
    return simplejson.loads(content)

def fetch_tracts_by_state(state):
    url = '%s/%s/tracts.jsonp' % (settings.API_URL, state)
    return _api_fetch(url)

def fetch_tracts_by_county(county):
    state = county[0:2]
    url = '%s/%s/tracts_%s.jsonp' % (settings.API_URL, state, county)
    return _api_fetch(url)

def fetch_county_subdivisions_by_county(county):
    state = county[0:2]
    url = '%s/%s/county_subdivisions_%s.jsonp' % (settings.API_URL, state, county)
    return _api_fetch(url)

def fetch_counties_by_state(state):
    url = '%s/%s/counties.jsonp' % (settings.API_URL, state)
    return _api_fetch(url)

def fetch_county_subdivisions_by_state(state):
    url = '%s/%s/county_subdivisions.jsonp' % (settings.API_URL, state)
    return _api_fetch(url)

def fetch_places_by_state(state):
    url = '%s/%s/places.jsonp' % (settings.API_URL, state)
    return _api_fetch(url)

def fetch_geography(geoid):
    state = geoid[0:2]
    url = '%s/%s/%s.jsonp' % (settings.API_URL, state, geoid)
    return _api_fetch(url)

def fetch_geographies(geoids):
    return [fetch_geography(geoid) for geoid in geoids]

def fetch_labels(dataset):
    url = '%s/%s_labels.jsonp' % (settings.API_URL, dataset)
    return _api_fetch(url)
 
