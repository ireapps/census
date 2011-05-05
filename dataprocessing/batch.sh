#!/bin/bash

# NO NATIONAL DATA!!!

# 2010
wget http://www2.census.gov/census_2010/redistricting_file--pl_94-171/Illinois/il2010.pl.zip
unzip il2010.pl.zip

wget http://www2.census.gov/census_2010/redistricting_file--pl_94-171/PL2010_Access2003.mdb
mdb-export PL2010_Access2003.mdb PL_Part1 >> PL2010_Part1.csv
mdb-export PL2010_Access2003.mdb PL_Geo_Header >> PL2010_Geo_Header.csv

rm il000012010.csv
cat PL2010_Part1.csv > il000012010.csv
cat il000012010.pl >> il000012010.csv

in2csv -f fixed -s census2010_geo_schema.csv ilgeo2010.pl > ilgeo2010.csv

# Crosswalk

wget http://www.census.gov/geo/www/2010census/tract_rel/trf_txt/us2010trf.txt
echo "STATE00,COUNTY00,TRACT00,GEOID00,POP00,HU00,PART00,AREA00,AREALAND00,STATE10,COUNTY10,TRACT10,GEOID10,POP10,HU10,PART10,AREA10,AREALAND10,AREAPT,AREALANDPT,AREAPCT00PT,AREALANDPCT00PT,AREAPCT10PT,AREALANDPCT10PT,POP10PT,POPPCT00,POPPCT10,HU10PT,HUPCT00,HUPCT10" > us2010trf.csv
cat us2010trf.txt >> us2010trf.csv

# 2000
wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/Illinois/il00001.upl.zip
unzip il00001.upl.zip

wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/Illinois/ilgeo.upl.zip
unzip ilgeo.upl.zip

wget http://www2.census.gov/census_2000/datasets/redistricting_file--pl_94-171/0File_Structure/Access2000/PL2000_Access2000.mdb
mdb-export PL2000_Access2000.mdb PL_Part1 > PL2000_Part1.csv
mdb-export PL2000_Access2000.mdb PL_Geo_Header > PL2000_Geo_Header.csv

rm il000012000.csv
cat PL2000_Part1.csv > il000012000.csv
cat il00001.upl >> il000012000.csv

in2csv -f fixed -s census2000_geo_schema.csv ilgeo.upl > ilgeo2000.csv

