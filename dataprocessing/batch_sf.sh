#!/bin/bash

if [ $# \< 2 ]
then
    echo "You must specify 'staging' or production' and the the proper-case name of a state as arguments, e.g. 'batch_sf.sh staging Delaware'."
    exit
fi

STATE_NAME=$1
STATE_NAME_LOWER=`echo $1 | tr '[A-Z]' '[a-z]'`
STATE_NAME_ABBR=`python get_state_abbr.py $1`
STATE_FIPS=`python get_state_fips.py $1`
ENVIRONMENT=$2
FAKE=$3

echo 'Dropping previous data.'
./__drop_database.sh

echo 'Ensuring mongo indexes.'
./ensure_indexes.sh

echo 'Fetching data'
#./fetch_sf_data_2000.sh $STATE_NAME $STATE_NAME_LOWER $STATE_NAME_ABBR
#./fetch_sf_data_2010.sh $STATE_NAME $STATE_NAME_LOWER $STATE_NAME_ABBR

echo 'Loading 2000 geographies'
./load_sf_geographies_2000.py data/${STATE_NAME_ABBR}geo2000.csv

echo 'Loading 2000 data'
# TODO == 47
for i in {1..3}
do
    ./load_sf_data_2000.py data/sf_data_2000_${STATE_NAME_LOWER}_$i.csv
    echo "skipping"
done

echo 'Loading labels'
./load_sf_labels_2010.py sf1_2010_data_labels.csv

if [ "$FAKE" = "FAKE" ]; then
    # Load 2000 headers as 2010 so fake 2010 data will match to shapes
    GEOGRAPHY_HEADER_2010=data/${STATE_NAME_ABBR}geo2000.csv
else
    GEOGRAPHY_HEADER_2010=data/${STATE_NAME_ABBR}geo2010.csv
fi

echo 'Loading 2010 geographies'
./load_sf_geographies_2010.py $GEOGRAPHY_HEADER_2010 
   
echo 'Loading crosswalk'
if [ "$FAKE" = "FAKE" ]; then
    ./load_crosswalk.py $STATE_FIPS $FAKE
else
    ./load_crosswalk.py $STATE_FIPS data/us2010trf.csv
fi

echo 'Loading 2010 data'
# TODO == 47
for i in {1..3}
do
    if [ "$FAKE" = "FAKE" ]; then
        # Load 2000 data as 2010 for testing
        ./load_sf_data_2010.py data/sf_data_2000_${STATE_NAME_LOWER}_$i.csv
    else
        ./load_sf_data_2010.py data/sf_data_2010_${STATE_NAME_LOWER}_$i.csv
    fi
done

echo 'Processing crosswalk'
./crosswalk.py $STATE_FIPS

echo 'Computing deltas'
./compute_deltas_sf.py $STATE_FIPS

echo 'Deploying to S3'
./deploy_data.py $ENVIRONMENT
./deploy_lookups.py $ENVIRONMENT
./deploy_labels.py $ENVIRONMENT

