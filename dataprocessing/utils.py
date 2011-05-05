#!/usr/bin/env python

SUMLEV_NATION = '010'
SUMLEV_STATE = '040'
SUMLEV_COUNTY = '050'
SUMLEV_TRACT = '140'
SUMLEV_PLACE = '160'

def geoid_nation(r):
    # TODO
    return ''

def geoid_state(r):
    return r['STATE']

def geoid_county(r):
    return r['STATE'] + r['COUNTY']

def geoid_tract(r):
    return r['STATE'] + r['COUNTY'] + r['TRACT']

def geoid_place(r):
    return r['STATE'] + r['PLACE']

GEOID_COMPUTERS = {
    SUMLEV_NATION: geoid_nation,
    SUMLEV_STATE: geoid_state,
    SUMLEV_COUNTY: geoid_county,
    SUMLEV_TRACT: geoid_tract,
    SUMLEV_PLACE: geoid_place,
}

def find_geography_by_xref(collection, xref):
    return collection.find_one({ "xrefs": { "$elemMatch": xref } })

def xref_from_row_dict(d):
    # Strip off unncessary attrs
    d.pop('CHARITER')
    d.pop('CIFSN')

    return { 
        'FILEID': d.pop('FILEID'),
        'STUSAB': d.pop('STUSAB'),
        'LOGRECNO': d.pop('LOGRECNO')
    }
