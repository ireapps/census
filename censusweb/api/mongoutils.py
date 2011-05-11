from django.conf import settings
from pymongo import Connection, ASCENDING

from constants import *

def get_geographies_collection():
    connection = Connection()
    db = connection[settings.CENSUS_DB] 
    return db[settings.GEOGRAPHIES_COLLECTION]

def get_labels_collection():
    connection = Connection()
    db = connection[settings.CENSUS_DB] 
    return db[settings.LABELS_COLLECTION]

def get_counties_by_state(state):
    geographies = get_geographies_collection()

    counties = geographies.find({ 'metadata.STATE': FIPS_CODES[state], 'sumlev': SUMLEV_COUNTY }, fields=['metadata.STATE', 'metadata.COUNTY', 'metadata.NAME'], sort=[('metadata.NAME', ASCENDING)])

    return [(c['metadata']['NAME'], c['metadata']['COUNTY'], c['metadata']['STATE']) for c in counties] 

def get_places_by_state(state):
    geographies = get_geographies_collection()

    places = geographies.find({ 'metadata.STATE': FIPS_CODES[state], 'sumlev': SUMLEV_PLACE }, fields=['metadata.STATE', 'metadata.PLACE', 'metadata.NAME'], sort=[('metadata.NAME', ASCENDING)])

    return [(p['metadata']['NAME'], p['metadata']['STATE'] + p['metadata']['PLACE']) for p in places] 

def get_tracts_by_county(fips):
    state_fips  = fips[0:2]
    county_fips = fips[2:]

    geographies = get_geographies_collection()

    tracts = geographies.find({ 'metadata.STATE': state_fips, 'metadata.COUNTY': county_fips, 'sumlev': SUMLEV_TRACT }, fields=['metadata.NAME', 'metadata.TRACT'], sort=[('metadata.NAME', ASCENDING)])

    return [(t['metadata']['NAME'], t['metadata']['TRACT']) for t in tracts] 

def get_geographies(state, county=None, tract=None):
    geographies = get_geographies_collection()

    lookup = {}
    lookup['metadata.STATE'] = FIPS_CODES[state]

    if county:
        lookup['metadata.COUNTY'] = county

    if tract:
        lookup['metadata.TRACT'] = tract

    return geographies.find(lookup)

def get_labels_for_table(year, table):
    labels = get_labels_collection()

    return labels.find_one({ 'year': year, 'key': table })

