#!/usr/bin/env python

import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import config
import utils

from csvkit.unicsv import UnicodeCSVWriter
from tempfile import mkdtemp
import os.path

METADATA_HEADERS = ['COUNTY', 'CBSA', 'CSA', 'NECTA', 'CNECTA', 'NAME', 'POP100', 'HU100']

def initialize_writer_dict(tempdir):
    d = {}
    sf1_data = utils.get_label_collection().find_one({'dataset': 'SF1'})
    for table_id, metadata in sf1_data['tables'].items():
        header = ['GEOID'] + METADATA_HEADERS
        for key in sorted(metadata['labels']):
            header.extend([key,"%s.2000" % key])
        path = os.path.join(tempdir,"%s.csv" % table_id)
        f = open(path,"w")
        w = UnicodeCSVWriter(f)
        w.writerow(header)
        d[table_id] = {'path': path, 'file': f, 'writer': w, 'labels': sorted(metadata['labels'])}

def add_rows_for_geography(writer_dict, geography):
    base_row = [geography['geoid']]
    for h in METADATA_HEADERS:
        base_row.append(geography['metadata'][h])

    for table_id in writer_dict:
        labels = writer_dict[table_id]['labels']
        row = base_row[:] # clone it so we don't append upon append...

        for l in labels:
            row.append(geography['data']['2010'][table_id][l])
            try:
                row.append(geography['data']['2000'][table_id][l])
            except:
                row.append('')

        writer_dict[table_id]['writer'].writerow(row)

# BEGIN MAIN OPERATION
if len(sys.argv) < 3:
    sys.exit('You must specify exactly 3 arguments to this script.\n%% %s [2 digit state FIPS code] [3 digit summary level] [staging|production]' % sys.argv[0])

STATE_FIPS = sys.argv[1]
SUMLEV = sys.argv[2]
ENVIRONMENT = sys.argv[3]

if SUMLEV not in config.SUMLEVS:
    sys.exit("Second argument must be a valid summary level as defined in config.SUMLEVS")

# TODO 
# this needs to be findable... ${DATAPROCESSING_DIR}/sf1_2010_data_labels.csv
# reduce duplication between make_sf_data_2010_headers.py and utils.py
# import a padded_label from utils... 
collection = utils.get_geography_collection()

tempdir = mkdtemp()
writer_dict = initialize_writer_dict(tempdir)

for geography in collection.find({'sumlev': SUMLEV, 'metadata.STATE': STATE_FIPS }):
    add_rows_for_geography(writer_dict,geography)
    row_count += 1

paths = dict((k,v['path']) for k,v in writer_dict.items())

for table_id in writer_dict: 
    writer_dict[table_id]['file'].close()
    writer_dict[table_id] = None
    
c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

# for thing in the writer_dict
deployed = 0

d = { 'state_fips': STATE_FIPS, 'sumlev': SUMLEV }
for table_id,path in paths.items():
    d['table_id'] = table_id
    k = Key(bucket)
    k.key = '%(state_fips)s/all_%(sumlev)s_in_%(state_fips)s.%(table_id)s.csv' % (d)
    data = open(path).read()
    compressed = utils.gzip_data(data)

    k.set_contents_from_string(compressed, headers={ 'Content-encoding': 'gzip', 'Content-Type': 'text/csv' }, policy='private')

    deployed += 1
    if deployed % 100 == 0:
        print 'Deployed %i...' % deployed

print 'Deployed: %i csvs for State %s Sumlev %s' % (deployed,STATE_FIPS,SUMLEV)

