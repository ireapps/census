#!/bin/bash

if [ $# \< 2 ]
then
    echo "You must specify exactly two arguments: (1) the proper-case name of a state, (2) 'staging' or production' e.g. 'batch_sf.sh Delaware staging'."
    exit
fi

STATE_NAME="${@:1:1}"
STATE_NAME_SPACE_FIXED=`echo "${STATE_NAME}" | tr '[ ]' '[_]'`
STATE_NAME_LOWER=`echo "${STATE_NAME}" | tr '[A-Z ]' '[a-z_]'`
STATE_NAME_ABBR=`python get_state_abbr.py "${STATE_NAME}"` || exit $?
STATE_FIPS=`python get_state_fips.py "${STATE_NAME}"` || exit $?
ENVIRONMENT="${@:2:1}"
FAKE="${@:3:1}"

echo Begin $STATE_NAME at `date`
echo 'Dropping previous data.'
./__drop_database.sh

echo 'Ensuring mongo indexes.'
./ensure_indexes.sh

echo 'Fetching data'
./fetch_sf_data_2000.sh "$STATE_NAME_SPACE_FIXED" "$STATE_NAME_LOWER" "$STATE_NAME_ABBR"
./fetch_sf_data_2010.sh "$STATE_NAME_SPACE_FIXED" "$STATE_NAME_LOWER" "$STATE_NAME_ABBR"

echo 'Loading 2000 geographies'
./load_sf_geographies_2000.py data/${STATE_NAME_ABBR}geo2000.csv || exit $?

echo 'Loading 2000 data'
for i in {1..39}
do
    ./load_sf_data_2000.py data/sf_data_2000_${STATE_NAME_LOWER}_$i.csv 
done

echo 'Loading labels'
./load_sf_labels_2010.py sf1_2010_data_labels.csv || exit $?

if [ "$FAKE" = "FAKE" ]; then
    # Load 2000 headers as 2010 so fake 2010 data will match to shapes
    GEOGRAPHY_HEADER_2010=data/${STATE_NAME_ABBR}geo2000.csv
else
    GEOGRAPHY_HEADER_2010=data/${STATE_NAME_ABBR}geo2010.csv
fi

echo 'Loading 2010 geographies'
./load_sf_geographies_2010.py $GEOGRAPHY_HEADER_2010 || exit $?
   
echo 'Loading crosswalk'
if [ "$FAKE" = "FAKE" ]; then
    ./load_crosswalk.py $STATE_FIPS $FAKE || exit $?
else
    ./load_crosswalk.py $STATE_FIPS data/us2010trf.csv || exit $?
fi

echo 'Loading 2010 data'
for i in {1..47}
do
    if [ "$FAKE" = "FAKE" ]; then
        # Load 2000 data as 2010 for testing
        ./load_sf_data_2010.py data/sf_data_2000_${STATE_NAME_LOWER}_$i.csv
    else
        ./load_sf_data_2010.py data/sf_data_2010_${STATE_NAME_LOWER}_$i.csv
    fi
done

echo 'Processing crosswalk'
./crosswalk.py || exit $?

echo 'Computing deltas'
./compute_deltas_sf.py || exit $?

echo 'Deploying to S3'
./deploy_data.py $ENVIRONMENT || exit $?
./deploy_lookups.py $ENVIRONMENT || exit $?
./deploy_labels.py $ENVIRONMENT || exit $?
./deploy_csv.py $STATE_FIPS 040 $ENVIRONMENT || exit $?
./deploy_csv.py $STATE_FIPS 050 $ENVIRONMENT || exit $?
./deploy_csv.py $STATE_FIPS 060 $ENVIRONMENT || exit $?
./deploy_csv.py $STATE_FIPS 140 $ENVIRONMENT || exit $?
./deploy_csv.py $STATE_FIPS 160 $ENVIRONMENT || exit $?
echo Complete $STATE_NAME at `date`

