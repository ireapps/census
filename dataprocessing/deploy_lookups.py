#!/usr/bin/env python

import json
import zlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pymongo import Connection

import config

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKET)

def push(key, obj):
    k = Key(bucket)
    k.key = key
    k.set_contents_from_string(zlib.compress(json.dumps(obj)), headers={ 'Content-encoding': 'deflate', 'Content-Type': 'application/json' }, policy='public-read')

state = collection.find_one()['metadata']['STATE']

print 'Deploying counties lookup'
counties = collection.find({ 'sumlev': config.SUMLEV_COUNTY }, fields=['geoid', 'metadata.NAME', 'metadata.COUNTY'], sort=[('metadata.NAME', 1)]) 
counties = [(c['metadata']['NAME'], c['geoid']) for c in counties]
push('%s_counties.json' % state, counties)

print 'Deploying places lookup'
places = collection.find({ 'sumlev': config.SUMLEV_PLACE }, fields=['geoid', 'metadata.NAME'], sort=[('metadata.NAME', 1)]) 
places = [(c['metadata']['NAME'], c['geoid']) for c in places]
push('%s_places.json' % state, places)

counties = collection.find({ 'sumlev': config.SUMLEV_COUNTY }, fields=['geoid', 'metadata.NAME', 'metadata.COUNTY'], sort=[('metadata.NAME', 1)]) 

for county in counties:
    print 'Deploying tracts lookup for %s' % county['metadata']['NAME']
    tracts = collection.find({ 'sumlev': config.SUMLEV_TRACT, 'metadata.COUNTY': county['metadata']['COUNTY'] }, fields=['geoid', 'metadata.NAME'], sort=[('metadata.NAME', 1)]) 
    tracts = [(c['metadata']['NAME'], c['geoid']) for c in tracts]
    print '%s_tracts.json' % (county['geoid'])
    push('%s_tracts.json' % (county['geoid']), tracts)

