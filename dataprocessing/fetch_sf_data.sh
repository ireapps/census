#!/bin/bash

STATE_NAME=$1
STATE_NAME_LOWER=$2
STATE_NAME_ABBR=$3
FAKE=$4

rm -r data
mkdir data
cd data

# 2000
wget http://www2.census.gov/census_2000/datasets/Summary_File_1/${STATE_NAME}/${STATE_NAME_ABBR}00001_uf1.zip
unzip ${STATE_NAME_ABBR}00001_uf1.zip

wget http://www2.census.gov/census_2000/datasets/Summary_File_1/${STATE_NAME}/${STATE_NAME_ABBR}geo_uf1.zip
unzip ${STATE_NAME_ABBR}geo_uf1.zip

wget http://www.census.gov/support/2000/SF1/Access97.zip
unzip Access97.zip
mdb-export SF1.mdb SF10001 > sf_data_2000_headers_1.csv
mdb-export SF1.mdb TABLES > sf_2000_data_labels.csv

rm sf_data_2000_${STATE_NAME_LOWER}_1.csv
cat sf_data_2000_headers_1.csv > sf_data_2000_${STATE_NAME_LOWER}_1.csv
cat ${STATE_NAME_ABBR}00001.uf1 >> sf_data_2000_${STATE_NAME_LOWER}_1.csv

in2csv -f fixed -s ../census2000_geo_schema.csv ${STATE_NAME_ABBR}geo.uf1 > ${STATE_NAME_ABBR}geo2000.csv

# 2010

# Load 2000 data as 2010 for testing
if [ "$FAKE" = "FAKE" ]; then
    cp sf_data_2000_${STATE_NAME_ABBR}_1.csv sf_data_2010_${STATE_NAME_ABBR}_1.csv
    cp ${STATE_NAME_ABBR}geo2000.csv ${STATE_NAME_ABBR}geo2010.csv
fi

