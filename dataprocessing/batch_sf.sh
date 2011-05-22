#!/bin/bash

# See batch.sh for notes.

STATE_NAME=$1
STATE_NAME_LOWER=`echo $1 | tr '[A-Z]' '[a-z]'`
STATE_NAME_ABBR=`python get_state_abbr.py $1`
STATE_FIPS=`python get_state_fips.py $1`
FAKE=$2

echo 'Ensuring mongo indexes.'
./ensure_indexes.sh

# echo 'Fetching data'
#./fetch_sf_data.sh $STATE_NAME $STATE_NAME_LOWER $STATE_NAME_ABBR

echo 'Loading 2000 geographies'
./load_sf_geographies_2000.py data/${STATE_NAME_ABBR}geo2000.csv

echo 'Loading 2000 data'
for i in {1..39}
do
    ./load_sf_data_2000.py data/sf_data_2000_${STATE_NAME_LOWER}_$i.csv
done

# Load 2000 data as 2010 for testing
if [ "$FAKE" = "FAKE" ]; then
    # echo 'Loading TODO labels'
    #./load_sf_labels_2000.py data/sf_2000_data_labels.csv

    echo 'Loading 2010 geographies'
    ./load_sf_geographies_2010.py data/${STATE_NAME_ABBR}geo2000.csv

    echo 'Loading crosswalk'
    ./load_crosswalk.py $STATE_FIPS $FAKE 

    echo 'Loading 2010 data'
    for i in {1..39}
    do
        ./load_sf_data_2010.py data/sf_data_2000_${STATE_NAME_LOWER}_$i.csv
    done

    echo 'Processing crosswalk'
    ./crosswalk.py $STATE_FIPS

    echo 'Computing deltas'
    ./compute_deltas.py $STATE_FIPS
fi
