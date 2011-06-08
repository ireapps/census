#!/bin/bash

STATE_NAME=$1
STATE_NAME_LOWER=$2
STATE_NAME_ABBR=$3

rm -r data
mkdir data
cd data

# 2000
for i in {1..39}
do
    FILE_NUMBER=`printf "%05d" $i`
    wget http://www2.census.gov/census_2000/datasets/Summary_File_1/${STATE_NAME}/${STATE_NAME_ABBR}${FILE_NUMBER}_uf1.zip
    unzip ${STATE_NAME_ABBR}${FILE_NUMBER}_uf1.zip
done

wget http://www2.census.gov/census_2000/datasets/Summary_File_1/${STATE_NAME}/${STATE_NAME_ABBR}geo_uf1.zip
unzip ${STATE_NAME_ABBR}geo_uf1.zip

wget http://www.census.gov/support/2000/SF1/Access97.zip
unzip Access97.zip

for i in {1..39}
do
    TABLE_NUMBER=`printf "%04d" $i`
    mdb-export SF1.MDB SF1${TABLE_NUMBER} > sf_data_2000_headers_$i.csv
done

mdb-export SF1.MDB TABLES > sf_2000_data_labels.csv

for i in {1..39}
do
    FILE_NUMBER=`printf "%05d" $i`
    rm sf_data_2000_${STATE_NAME_LOWER}_$i.csv
    cat sf_data_2000_headers_$i.csv > sf_data_2000_${STATE_NAME_LOWER}_$i.csv
    cat ${STATE_NAME_ABBR}${FILE_NUMBER}.uf1 >> sf_data_2000_${STATE_NAME_LOWER}_$i.csv
done

in2csv -f fixed -s ../census2000_geo_schema.csv ${STATE_NAME_ABBR}geo.uf1 > ${STATE_NAME_ABBR}geo2000.csv

# 2010

wget http://www2.census.gov/census_2010/redistricting_file--pl_94-171/${STATE_NAME}/${STATE_NAME_ABBR}2010.pl.zip
unzip ${STATE_NAME_ABBR}2010.pl.zip

in2csv -f fixed -s ../census2010_geo_schema.csv ${STATE_NAME_ABBR}geo2010.pl > ${STATE_NAME_ABBR}geo2010.csv

# Crosswalk

wget http://www.census.gov/geo/www/2010census/tract_rel/trf_txt/us2010trf.txt
echo "STATE00,COUNTY00,TRACT00,GEOID00,POP00,HU00,PART00,AREA00,AREALAND00,STATE10,COUNTY10,TRACT10,GEOID10,POP10,HU10,PART10,AREA10,AREALAND10,AREAPT,AREALANDPT,AREAPCT00PT,AREALANDPCT00PT,AREAPCT10PT,AREALANDPCT10PT,POP10PT,POPPCT00,POPPCT10,HU10PT,HUPCT00,HUPCT10" > us2010trf.csv
cat us2010trf.txt >> us2010trf.csv
