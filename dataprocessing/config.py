#!/usr/bin/env python

# Geocomp value declaring a row is not a geographic compontent
GEOCOMP_COMPLETE = '00'

# Summary level constants
SUMLEV_NATION = '010'
SUMLEV_STATE = '040'
SUMLEV_COUNTY = '050'
SUMLEV_COUNTY_SUBDIVISION = '060'
SUMLEV_TRACT = '140'
SUMLEV_PLACE = '160'
SUMLEV_BLOCK = '101'

# Summary levels to load
SUMLEVS = [SUMLEV_TRACT]

# Mongo
CENSUS_DB = 'census'
LABELS_DB = 'census_labels'
GEOGRAPHIES_COLLECTION = 'geographies'
GEOGRAPHIES_2000_COLLECTION = 'geographies_2000'
LABELS_COLLECTION = 'labels'

# S3
S3_BUCKETS = {
    'staging': 'census-test',
    'production': 'censusdata.ire.org',
}
