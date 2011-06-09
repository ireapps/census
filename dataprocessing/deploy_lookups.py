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

def push(slug, obj):
    k = Key(bucket)
    k.key = '%s.jsonp' % slug
    data = json.dumps(obj)
    jsonp = '%s(%s)' % (slug, data) 
    k.set_contents_from_string(zlib.compress(jsonp), headers={ 'Content-encoding': 'deflate', 'Content-Type': 'application/javascript' }, policy='public-read')

state = collection.find_one()['metadata']['STATE']

print 'Deploying counties lookup'
counties = collection.find({ 'sumlev': config.SUMLEV_COUNTY }, fields=['geoid', 'metadata.NAME', 'metadata.COUNTY'], sort=[('metadata.NAME', 1)]) 
counties = [(c['metadata']['NAME'], c['geoid']) for c in counties]
push('counties_%s' % state, counties)

print 'Deploying places lookup'
places = collection.find({ 'sumlev': config.SUMLEV_PLACE }, fields=['geoid', 'metadata.NAME'], sort=[('metadata.NAME', 1)]) 
places = [(c['metadata']['NAME'], c['geoid']) for c in places]
push('places_%s' % state, places)

counties = collection.find({ 'sumlev': config.SUMLEV_COUNTY }, fields=['geoid', 'metadata.NAME', 'metadata.COUNTY'], sort=[('metadata.NAME', 1)]) 

for county in counties:
    print 'Deploying counties subdivisions lookup for %s' % county['metadata']['NAME']
    county_subdivisions = collection.find({ 'sumlev': config.SUMLEV_COUNTY_SUBDIVISION }, fields=['geoid', 'metadata.NAME', 'metadata.COUNTY_SUBDIVISION'], sort=[('metadata.NAME', 1)]) 
    county_subdivisions = [(c['metadata']['NAME'], c['geoid']) for c in county_subdivisions]
    push('county_subdivisions_%s' % county['geoid'], county_subdivisions)

    print 'Deploying tracts lookup for %s' % county['metadata']['NAME']
    tracts = collection.find({ 'sumlev': config.SUMLEV_TRACT, 'metadata.COUNTY': county['metadata']['COUNTY'] }, fields=['geoid', 'metadata.NAME'], sort=[('metadata.NAME', 1)]) 
    tracts = [(c['metadata']['NAME'], c['geoid']) for c in tracts]
    push('tracts_%s' % county['geoid'], tracts)

