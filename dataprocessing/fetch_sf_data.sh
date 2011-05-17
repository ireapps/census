#!/bin/bash

# NO NATIONAL DATA!!!

rm -r data
mkdir data
cd data

# 2000 - DELAWARE - SF1
wget http://www2.census.gov/census_2000/datasets/Summary_File_1/Delaware/de00001_uf1.zip
unzip de00001_uf1.zip

wget http://www2.census.gov/census_2000/datasets/Summary_File_1/Delaware/degeo_uf1.zip
unzip degeo_uf1.zip

wget http://www.census.gov/support/2000/SF1/Access97.zip
unzip Access97.zip
mdb-export SF1.mdb SF10001 > sf_data_2000_headers_1.csv
mdb-export SF1.mdb TABLES > sf_2000_data_labels.csv

rm sf_data_2000_delaware_1.csv
cat sf_data_2000_headers_1.csv > sf_data_2000_delaware_1.csv
cat de00001.uf1 >> sf_data_2000_delaware_1.csv

in2csv -f fixed -s ../census2000_geo_schema.csv degeo.uf1 > degeo2000.csv
