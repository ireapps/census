#!/usr/bin/env python

# Summary level constants
SUMLEV_NATION = '010'
SUMLEV_STATE = '040'
SUMLEV_COUNTY = '050'
SUMLEV_TRACT = '140'
SUMLEV_PLACE = '160'

# Summary levels to load
# TODO: load everything
SUMLEVS = [SUMLEV_STATE, SUMLEV_COUNTY, SUMLEV_TRACT]

# 2000
PL_2000_GEOGRAPHIES_FILENAME = 'data/ilgeo2000.csv'
PL_2000_FILENAME = 'data/il000012000.csv'

# 2010
PL_2010_GEOGRAPHIES_FILENAME = 'data/ilgeo2010.csv'
PL_2010_FILENAME = 'data/il000012010.csv'
DPSF_2010_FILENAME = 'data/ri000012010.csv'

# Crosswalk
CROSSWALK_FILENAME = 'data/us2010trf.csv'

# Mongo
CENSUS_DB = 'census'
GEOGRAPHIES_COLLECTION = 'geographies'
GEOGRAPHIES_2000_COLLECTION = 'geographies_2000'

