#!/bin/bash

DATA_DIR=$1
STATE_FIPS_CODES=${@:2}

start_dir=`pwd`

for STATE_FIPS_CODE in $STATE_FIPS_CODES
do
    mkdir -p "${DATA_DIR}/STATE"
    cd "${DATA_DIR}/STATE"
    wget "ftp://ftp2.census.gov/geo/tiger/TIGER2010/STATE/2010/tl_2010_${STATE_FIPS_CODE}_state10.zip"

    cd $start_dir

    mkdir -p "${DATA_DIR}/COUNTY"
    cd "${DATA_DIR}/COUNTY"
    wget "ftp://ftp2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_${STATE_FIPS_CODE}_county10.zip"

    cd $start_dir

    mkdir -p "${DATA_DIR}/PLACE"
    cd "${DATA_DIR}/PLACE"
    wget "ftp://ftp2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_${STATE_FIPS_CODE}_place10.zip"

    cd $start_dir

    mkdir -p "${DATA_DIR}/TRACT"
    cd "${DATA_DIR}/TRACT"
    wget "ftp://ftp2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_${STATE_FIPS_CODE}_tract10.zip"

    cd $start_dir

    mkdir -p "${DATA_DIR}/COUSUB"
    cd "${DATA_DIR}/COUSUB"
    wget "ftp://ftp2.census.gov/geo/tiger/TIGER2010/COUSUB/2010/tl_2010_${STATE_FIPS_CODE}_cousub10.zip"

    cd $start_dir

done
echo "Done"

