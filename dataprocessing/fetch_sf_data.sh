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

