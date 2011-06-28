#!/usr/bin/env python

from StringIO import StringIO
import gzip
import re

import config

TABLE_NAME_REGEX = re.compile('([A-Z1-9]+?)0*([\d]+)([A-Z]?)')
TABLE_ID_PATTERN = re.compile(r'^(?P<letter>[A-Z]+)(?P<number>\d+)(?P<suffix>[A-Z])?')

def parse_table_id(table_id):
    return TABLE_ID_PATTERN.match(table_id).groupdict()

def generate_stat_key(table_id, line):
    """Pad and connect table and line number to get a standard identifier for a statistic."""
    d = parse_table_id(table_id)
    if d['suffix'] is None: d['suffix'] = ''
    d['number'] = int(d['number'])
    d['line'] = line
    return "%(letter)s%(number)03i%(suffix)s%(line)03i" % d
        
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
    return collection.find_one({ 'xrefs.FILEID': xref['FILEID'], 'xrefs.STUSAB': xref['STUSAB'], 'xrefs.LOGRECNO': xref['LOGRECNO'] }, fields=fields)

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

def gzip_data(d):
    s = StringIO()
    gz = gzip.GzipFile(fileobj=s, mode='wb')
    gz.write(d)
    gz.close()

    return s.getvalue()

def gunzip_data(d):
    s = StringIO(d)
    gz = gzip.GzipFile(fileobj=s, mode='rb')
    
    content = gz.read()
    gz.close()

    return content
