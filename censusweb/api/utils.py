#!/usr/bin/env python

import simplejson

from sqlalchemy import Column, MetaData, Table
from sqlalchemy import Float, Integer, String
from sqlalchemy.schema import CreateTable

from api import mongoutils

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

LINKING_COLUMNS = [
    ('FILEID',6),
    ('STUSAB',2),
    ('CHARITER',3),
    ('CIFSN',3),
    ('LOGRECNO',7),
]    

def generate_create_sql_by_file(file_numbers=None):
    if file_numbers is None:
        file_numbers = range(1,48)

    statements = []
    for file_number in file_numbers:
        sql_table = _create_base_table(_table_name_for_number(file_number))
        for table in SF1_FILE_SEGMENTS[file_number]:
            _add_sql_columns_for_table(sql_table,table)
        statements.append(unicode(CreateTable(sql_table).compile(dialect=None)).strip() + ';')

    return "\n\n".join(statements)

def _table_name_for_number(file_number):
    return 'sf1_%02i' % file_number

def generate_sql_by_table(table_codes=None):
    statements = []
    if table_codes is None:
        table_codes = []
        for f in SF1_FILE_SEGMENTS[1:]:
            table_codes.extend(f)

    statements = []
    for table_code in table_codes:
        sql_table = _create_base_table(table_code)
        _add_sql_columns_for_table(sql_table,table_code)
        statements.append(unicode(CreateTable(sql_table).compile(dialect=None)).strip() + ';')
    
    return "\n\n".join(statements)

def generate_views_by_table(table_codes=None):
    labels = mongoutils.get_labelset()

    statements = []
    if table_codes is None:
        table_codes = []
        for f in SF1_FILE_SEGMENTS[1:]:
            table_codes.extend(f)

    statements = []
    for table_code in table_codes:
        table_name = _table_name_for_number(FILE_NUMBER_BY_TABLE_CODE[table_code])
        columns = ['"%s"' % x[0] for x in LINKING_COLUMNS]
        for label in sorted(labels['tables'][table_code]['labels']):
            columns.append('"%s"' % label)

        columns = ',\n'.join(columns)
        statements.append('CREATE VIEW sf1_%s as SELECT %s from %s;' % (table_code,columns,table_name))
    
    return "\n\n".join(statements)

def _create_base_table(name):
    metadata = MetaData()
    sql_table = Table(name, metadata)
    for name,length in LINKING_COLUMNS:
        sql_table.append_column(Column(name, String(length=length), nullable=False))

    return sql_table

def _add_sql_columns_for_table(sql_table,code):
    labels = mongoutils.get_labelset()
    table_labels = labels['tables'][code]
    if table_labels['name'].find('AVERAGE') != -1 or table_labels['name'].find('MEDIAN') != -1:
        col_type = Float
    else:
        col_type = Integer
    for label in sorted(table_labels['labels']):
        sql_table.append_column(Column(label, col_type(), nullable=False))

SF1_FILE_SEGMENTS = [
    [ 'no file zero, this is a place_holder'],
    ['P1'], # file 1
    ['P2'], # file 2
    ['P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9'], # file 3
    ['P10', 'P11', 'P12', 'P13', 'P14'], # file 4
    ['P15', 'P16', 'P17', 'P18', 'P19', 'P20', 'P21', 'P22', 'P23', 'P24', 'P25', 'P26', 'P27', 'P28', 'P29', 'P30'], # file 5
    ['P31', 'P32', 'P33', 'P34', 'P35', 'P36', 'P37', 'P38', 'P39', 'P40', 'P41', 'P42', 'P43', 'P44', 'P45', 'P46', 'P47', 'P48', 'P49'], # file 6
    ['P50', 'P51', 'P12A', 'P12B', 'P12C', 'P12D', 'P12E'], # file 7
    ['P12F', 'P12G', 'P12H', 'P12I', 'P13A', 'P13B', 'P13C', 'P13D', 'P13E', 'P13F', 'P13G', 'P13H', 'P13I', 'P16A', 'P16B', 'P16C', 'P16D', 'P16E', 'P16F', 'P16G', 'P16H', 'P16I', 'P17A'], # file 8
    ['P17B', 'P17C', 'P17D', 'P17E', 'P17F', 'P17G', 'P17H', 'P17I', 'P18A', 'P18B', 'P18C', 'P18D', 'P18E', 'P18F', 'P18G', 'P18H', 'P18I', 'P28A', 'P28B', 'P28C', 'P28D', 'P28E', 'P28F', 'P28G', 'P28H', 'P28I'], # file 9
    ['P29A', 'P29B', 'P29C', 'P29D', 'P29E', 'P29F', 'P29G', 'P29H', 'P29I'], # file 10
    ['P31A', 'P31B', 'P31C', 'P31D', 'P31E', 'P31F', 'P31G', 'P31H', 'P31I', 'P34A', 'P34B', 'P34C', 'P34D', 'P34E'], # file 11
    ['P34F', 'P34G', 'P34H', 'P34I', 'P35A', 'P35B', 'P35C', 'P35D', 'P35E', 'P35F', 'P35G', 'P35H', 'P35I', 'P36A', 'P36B', 'P36C', 'P36D', 'P36E', 'P36F', 'P36G', 'P36H', 'P36I', 'P37A', 'P37B', 'P37C', 'P37D', 'P37E', 'P37F', 'P37G', 'P37H', 'P37I', 'P38A', 'P38B', 'P38C', 'P38D', 'P38E'], # file 12
    ['P38F', 'P38G', 'P38H', 'P38I', 'P39A', 'P39B', 'P39C', 'P39D', 'P39E', 'P39F', 'P39G', 'P39H'], # file 13
    ['P39I'], # file 14
    ['PCT1', 'PCT2', 'PCT3', 'PCT4', 'PCT5', 'PCT6', 'PCT7', 'PCT8'], # file 15
    ['PCT9', 'PCT10', 'PCT11'], # file 16
    ['PCT12'], # file 17
    ['PCT13', 'PCT14', 'PCT15', 'PCT16', 'PCT17', 'PCT18', 'PCT19', 'PCT20'], # file 18
    ['PCT21','PCT22'], # file 19
    ['PCT12A'], # file 20
    ['PCT12B'], # file 21
    ['PCT12C'], # file 22
    ['PCT12D'], # file 23
    ['PCT12E'], # file 24
    ['PCT12F'], # file 25
    ['PCT12G'], # file 26
    ['PCT12H'], # file 27
    ['PCT12I'], # file 28
    ['PCT12J'], # file 29
    ['PCT12K'], # file 30
    ['PCT12L'], # file 31
    ['PCT12M'], # file 32
    ['PCT12N'], # file 33
    ['PCT12O'], # file 34
    ['PCT13A','PCT13B','PCT13C','PCT13D','PCT13E'], # file 35
    ['PCT13F','PCT13G','PCT13H','PCT13I','PCT14A','PCT14B','PCT14C','PCT14D','PCT14E','PCT14F','PCT14G','PCT14H','PCT14I','PCT19A','PCT19B'], # file 36
    ['PCT19C','PCT19D','PCT19E','PCT19F','PCT19G','PCT19H','PCT19I','PCT20A','PCT20B','PCT20C','PCT20D','PCT20E'], # file 37
    ['PCT20F','PCT20G','PCT20H','PCT20I','PCT22A','PCT22B','PCT22C','PCT22D','PCT22E','PCT22F'], # file 38
    ['PCT22G','PCT22H','PCT22I'], # file 39
    ['PCO1','PCO2','PCO3','PCO4','PCO5','PCO6'], # file 40
    ['PCO7','PCO8','PCO9','PCO10'], # file 41
    ['H1'], # file 42
    ['H2'], # file 43
    ['H3','H4','H5','H6','H7','H8','H9','H10','H11','H12','H13','H14','H15','H16','H17','H18','H19','H20','H21','H22','H11A','H11B', 'H11C','H11D', 'H11E','H11F'], # file 44
    ['H11G','H11H','H11I','H12A','H12B','H12C','H12D','H12E','H12F','H12G','H12H','H12I','H16A','H16B','H16C','H16D','H16E','H16F','H16G','H16H','H16I','H17A','H17B','H17C'], # file 45
    ['H17D','H17E','H17F','H17G','H17H','H17I'], # file 46
    ['HCT1','HCT2','HCT3','HCT4'], # file 47
]

FILE_NUMBER_BY_TABLE_CODE = {}
for i,x in enumerate(SF1_FILE_SEGMENTS):
    if i > 0:
        for table_code in x:
            FILE_NUMBER_BY_TABLE_CODE[table_code] = i

