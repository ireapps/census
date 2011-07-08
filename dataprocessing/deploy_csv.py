#!/usr/bin/env python

import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from cStringIO import StringIO

import config
import utils
import gzip

from csvkit.unicsv import UnicodeCSVWriter

def get_2000_top_level_counts(geography):
    try:
        pop2000 = geography['data']['2000']['P1']['P001001']
        hu2000 = geography['data']['2000']['H1']['H001001']
        return pop2000,hu2000
    except KeyError:
        return '',''
METADATA_HEADERS = ['STATE','COUNTY', 'CBSA', 'CSA', 'NECTA', 'CNECTA', 'NAME', 'POP100', 'HU100']
def deploy_table(state_fips,sumlev, bucket, table_id, metadata):
    query = {'sumlev': sumlev, 'metadata.STATE': state_fips }
    s = StringIO()
    gz = gzip.GzipFile(fileobj=s, mode='wb')
    w = UnicodeCSVWriter(gz)

    header = ['GEOID', 'SUMLEV'] + METADATA_HEADERS + ['POP100.2000','HU100.2000']
    for key in sorted(metadata['labels']):
        header.extend([key,"%s.2000" % key])

    w.writerow(header)

    for geography in collection.find(query):
        row = [geography['geoid'],geography['sumlev']]

        for h in METADATA_HEADERS:
            row.append(geography['metadata'][h])

        pop2000,hu2000 = get_2000_top_level_counts(geography)
        row.extend([pop2000,hu2000])

        for key in sorted(metadata['labels']):
            try:
                row.append(geography['data']['2010'][table_id][key])
            except KeyError, e:
                if table_id.startswith('PCO'):
                    print "No data for %s at %s" % (table_id, sumlev)
                    return
                raise e # don't otherwise expect this error, so raise it...
            try:
                row.append(geography['data']['2000'][table_id][key])
            except KeyError:
                row.append('')
        w.writerow(row)

    gz.close()
    query['table_id'] = table_id
    k = Key(bucket)
    k.key = '%(metadata.STATE)s/all_%(sumlev)s_in_%(metadata.STATE)s.%(table_id)s.csv' % (query)
    k.set_contents_from_string(s.getvalue(), headers={ 'Content-encoding': 'gzip', 'Content-Type': 'text/csv' }, policy='private')
    print "S3: wrote ",k.key," to ", ENVIRONMENT



def fetch_tables_and_labels():
    lc = utils.get_label_collection()
    return lc.find_one({'dataset': 'SF1'},fields=['tables'])['tables']
    
# BEGIN MAIN OPERATION
if __name__ == '__main__':
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

    c = S3Connection()
    bucket = c.get_bucket(config.S3_BUCKETS[ENVIRONMENT])

    for table_id in sorted(tables):
        metadata = tables[table_id]
        deploy_table(STATE_FIPS,SUMLEV,bucket, table_id, metadata)
        