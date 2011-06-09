#!/usr/bin/env python

import re

import config

TABLE_NAME_REGEX = re.compile('([A-Z1-9]+?)0*([\d]+)')

def geoid_nation(r):
    # TODO
    return ''

def geoid_state(r):
    return r['STATE']

def geoid_county(r):
    return r['STATE'] + r['COUNTY']

def geoid_county_subdivision(r):
    return r['STATE'] + r['COUNTY'] + r['COUSUB']

def geoid_tract(r):
    return r['STATE'] + r['COUNTY'] + r['TRACT']

def geoid_place(r):
    return r['STATE'] + r['PLACE']

def geoid_block(r):
    return r['STATE'] + r['COUNTY'] + r['TRACT'] + r['BLOCK']

GEOID_COMPUTERS = {
    config.SUMLEV_NATION: geoid_nation,
    config.SUMLEV_STATE: geoid_state,
    config.SUMLEV_COUNTY: geoid_county,
    config.SUMLEV_COUNTY_SUBDIVISION: geoid_county_subdivision,
    config.SUMLEV_TRACT: geoid_tract,
    config.SUMLEV_PLACE: geoid_place,
    config.SUMLEV_BLOCK: geoid_block,
}

def parse_table_from_key(key):
    t = key[0:-3]
    match = TABLE_NAME_REGEX.match(t)
    return ''.join(match.groups())

def find_geography_by_xref(collection, xref, fields=None):
    return collection.find_one({ 'xrefs': { '$elemMatch': xref } }, fields=fields)

def find_geographies_for_xwalk(collection, geography, fields=None):
    return collection.find({ 'geoid': { '$in': geography['xwalk'].keys() } }, fields=fields)

def xref_from_row_dict(d):
    # Strip off unncessary attrs
    d.pop('CHARITER')
    d.pop('CIFSN')

    return { 
        'FILEID': d.pop('FILEID'),
        'STUSAB': d.pop('STUSAB'),
        'LOGRECNO': d.pop('LOGRECNO')
    }
