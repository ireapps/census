#!/bin/bash

STATE_NAME=$1
STATE_NAME_LOWER=$2
STATE_NAME_ABBR=$3

EMBARGO_DOMAIN="https://www.census.gov/embargo/pio"
CENSUS_DOMAIN="http://www2.census.gov/census_2010/04-Summary_File_1/"

DATAPROCESSING_DIR=`pwd`

cd data

# 2010
wget $EMBARGO_DOMAIN/${STATE_NAME}/${STATE_NAME_ABBR}2010.sf1.zip --user $CENSUS_USER --password $CENSUS_PASS

if [ ! -f ${STATE_NAME_ABBR}2010.sf1.zip ]
then
    wget $CENSUS_DOMAIN/${STATE_NAME}/${STATE_NAME_ABBR}2010.sf1.zip --user $CENSUS_USER --password $CENSUS_PASS
fi

unzip ${STATE_NAME_ABBR}2010.sf1.zip

# Generate headers
${DATAPROCESSING_DIR}/make_sf_data_2010_headers.py ${DATAPROCESSING_DIR}/sf1_2010_data_labels.csv

for i in {1..47}
do
    FILE_NUMBER=`printf "%05d" $i`
    rm sf_data_2010_${STATE_NAME_LOWER}_$i.csv
    cat sf_data_2010_headers_$i.csv > sf_data_2010_${STATE_NAME_LOWER}_$i.csv
    cat ${STATE_NAME_ABBR}${FILE_NUMBER}2010.sf1 >> sf_data_2010_${STATE_NAME_LOWER}_$i.csv
done

in2csv -f fixed -s ${DATAPROCESSING_DIR}/census2010_geo_schema.csv ${STATE_NAME_ABBR}geo2010.sf1 > ${STATE_NAME_ABBR}geo2010.csv

