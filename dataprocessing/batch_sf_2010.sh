#!/bin/bash

if [ $# \< 2 ]
then
    echo "You must specify the proper-case name of a state as an argument, e.g. 'Delaware'."
    exit
fi

STATE_NAME=$1
STATE_NAME_LOWER=`echo $1 | tr '[A-Z]' '[a-z]'`
STATE_NAME_ABBR=`python get_state_abbr.py $1`
STATE_FIPS=`python get_state_fips.py $1`
FAKE=$2

# Load 2000 data as 2010 for testing
if [ "$FAKE" = "FAKE" ]; then
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

