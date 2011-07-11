#!/bin/bash

# NO NATIONAL DATA!!!

rm -r data/*
cd data

# 2000 - ILLINOIS - PL1 and PL2
wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/Illinois/il00001.upl.zip
unzip il00001.upl.zip

wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/Illinois/il00002.upl.zip
unzip il00002.upl.zip

wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/Illinois/ilgeo.upl.zip
unzip ilgeo.upl.zip

wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/0File_Structure/Access2000/PL2000_Access2000.mdb
mdb-export PL2000_Access2000.mdb PL_Part1 > pl_data_2000_headers_1.csv
mdb-export PL2000_Access2000.mdb PL_Part2 > pl_data_2000_headers_2.csv
mdb-export PL2000_Access2000.mdb tables > pl_2000_data_labels.csv

cat pl_data_2000_headers_1.csv > pl_data_2000_illinois_1.csv
cat il00001.upl >> pl_data_2000_illinois_1.csv

cat pl_data_2000_headers_2.csv > pl_data_2000_illinois_2.csv
cat il00002.upl >> pl_data_2000_illinois_2.csv

in2csv -f fixed -s ../census2000_geo_schema.csv ilgeo.upl > ilgeo2000.csv

# 2010 - ILLINOIS - PL1 and PL2
wget http://www2.census.gov/census_2010/redistricting_file--pl_94-171/Illinois/il2010.pl.zip
unzip il2010.pl.zip

wget http://www2.census.gov/census_2010/redistricting_file--pl_94-171/PL2010_Access2003.mdb
mdb-export PL2010_Access2003.mdb PL_Part1 >> pl_data_2010_headers_1.csv
mdb-export PL2010_Access2003.mdb PL_Part2 >> pl_data_2010_headers_2.csv
mdb-export PL2010_Access2003.mdb Table > pl_2010_data_labels.csv

cat pl_data_2010_headers_1.csv > pl_data_2010_illinois_1.csv
cat il000012010.pl >> pl_data_2010_illinois_1.csv

cat pl_data_2010_headers_2.csv > pl_data_2010_illinois_2.csv
cat il000022010.pl >> pl_data_2010_illinois_2.csv

in2csv -f fixed -s ../census2010_geo_schema.csv ilgeo2010.pl > ilgeo2010.csv

# Crosswalk

wget http://www.census.gov/geo/www/2010census/tract_rel/trf_txt/us2010trf.txt
echo "STATE00,COUNTY00,TRACT00,GEOID00,POP00,HU00,PART00,AREA00,AREALAND00,STATE10,COUNTY10,TRACT10,GEOID10,POP10,HU10,PART10,AREA10,AREALAND10,AREAPT,AREALANDPT,AREAPCT00PT,AREALANDPCT00PT,AREAPCT10PT,AREALANDPCT10PT,POP10PT,POPPCT00,POPPCT10,HU10PT,HUPCT00,HUPCT10" > us2010trf.csv
cat us2010trf.txt >> us2010trf.csv
