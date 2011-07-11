#!/bin/bash

if [ $# \< 2 ]
then
    echo "You must specify exactly two arguments: (1) the proper-case name of a state, (2) 'staging' or production' e.g. 'batch_pl.sh Delaware staging'."
    exit
fi

STATE_NAME="${@:1:1}"
STATE_NAME_SPACE_FIXED=`echo "${STATE_NAME}" | tr '[ ]' '[_]'`
STATE_NAME_LOWER=`echo "${STATE_NAME}" | tr '[A-Z ]' '[a-z_]'`
STATE_NAME_ABBR=`python get_state_abbr.py "${STATE_NAME}"` || exit $?
STATE_FIPS=`python get_state_fips.py "${STATE_NAME}"` || exit $?
ENVIRONMENT="${@:2:1}"

./__drop_database.sh

./ensure_indexes.sh

#./fetch_pl_data.sh

./load_pl_geographies_2000.py data/${STATE_NAME_ABBR}geo2000.csv
./load_pl_data_2000.py data/pl_data_2000_${STATE_NAME_LOWER}_1.csv
./load_pl_data_2000.py data/pl_data_2000_${STATE_NAME_LOWER}_2.csv

./load_pl_geographies_2010.py data/${STATE_NAME_ABBR}geo2010.csv

./load_crosswalk.py $STATE_FIPS data/us2010trf.csv
./load_pl_data_2010.py data/pl_data_2010_${STATE_NAME_LOWER}_1.csv
./load_pl_data_2010.py data/pl_data_2010_${STATE_NAME_LOWER}_2.csv

./load_pl_labels_2010.py data/pl_2010_data_labels.csv

./crosswalk.py $STATE_FIPS
./compute_deltas_pl.py $STATE_FIPS

#./deploy_data.py $ENVIRONMENT 
#./deploy_lookups.py $ENVIRONMENT
#./update_state_list.py $ENVIRONMENT $STATE_NAME CLEAR
#./make_state_public.py $ENVIRONMENT $STATE_NAME

#./test_pl.py
