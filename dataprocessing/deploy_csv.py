#!/usr/bin/env python

import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from cStringIO import StringIO

import config
import utils
import gzip

from csvkit.unicsv import UnicodeCSVWriter

METADATA_HEADERS = ['COUNTY', 'CBSA', 'CSA', 'NECTA', 'CNECTA', 'NAME', 'POP100', 'HU100']

def fetch_tables_and_labels():
    lc = utils.get_label_collection()
    return lc.find_one({'dataset': 'SF1'},fields=['tables'])['tables']
    
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

tables = fetch_tables_and_labels()

d = { 'state_fips': STATE_FIPS, 'sumlev': SUMLEV }
c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

for table_id,metadata in tables.items():
    s = StringIO()
    gz = gzip.GzipFile(fileobj=s, mode='wb')
    w = UnicodeCSVWriter(gz)

    header = ['GEOID'] + METADATA_HEADERS
    for key in sorted(metadata['labels']):
        header.extend([key,"%s.2000" % key])

    w.writerow(header)

    for geography in collection.find({'sumlev': SUMLEV, 'metadata.STATE': STATE_FIPS },fields=['geoid','metadata','data.2010.%s' % table_id,'data.2000.%s' % table_id]):
        row = [geography['geoid']]
        for h in METADATA_HEADERS:
            row.append(geography['metadata'][h])
        
        for key in sorted(metadata['labels']):
            row.append(geography['data']['2010'][table_id][key])
            try:
                row.append(geography['data']['2000'][table_id][key])
            except:
                row.append('')
        w.writerow(row)

    gz.close()
    d['table_id'] = table_id
    k = Key(bucket)
    k.key = '%(state_fips)s/all_%(sumlev)s_in_%(state_fips)s.%(table_id)s.csv' % (d)
    k.set_contents_from_string(s.getvalue(), headers={ 'Content-encoding': 'gzip', 'Content-Type': 'text/csv' }, policy='private')
    print "S3: wrote ",k.key," to ", ENVIRONMENT


