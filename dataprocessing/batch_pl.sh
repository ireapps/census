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

echo 'Dropping previous data.'
./__drop_database.sh || exit $?

echo 'Ensuring mongo indexes.'
./ensure_indexes.sh || exit $?

echo 'Fetching data'
./fetch_pl_data.sh "$STATE_NAME_SPACE_FIXED" "$STATE_NAME_LOWER" "$STATE_NAME_ABBR" "$STATE_FIPS" || exit $?

echo 'Loading 2000 geographies'
./load_pl_geographies_2000.py data/${STATE_NAME_ABBR}geo2000.csv || exit $?

echo 'Loading 2000 data'
./load_pl_data_2000.py data/pl_data_2000_${STATE_NAME_LOWER}_1.csv || exit $?
./load_pl_data_2000.py data/pl_data_2000_${STATE_NAME_LOWER}_2.csv || exit $?

echo 'Loading 2010 geographies'
./load_pl_geographies_2010.py data/${STATE_NAME_ABBR}geo2010.csv || exit $?

echo 'Loading crosswalk'
./load_crosswalk.py $STATE_FIPS data/us2010trf.csv || exit $?
./load_pl_data_2010.py data/pl_data_2010_${STATE_NAME_LOWER}_1.csv || exit $?
./load_pl_data_2010.py data/pl_data_2010_${STATE_NAME_LOWER}_2.csv || exit $?

echo 'Loading labels'
./load_pl_labels_2010.py data/pl_2010_data_labels.csv || exit $?

echo 'Processing crosswalk'
./crosswalk.py pl_field_mappings_2000_2010.csv pl_crosswalk_key.csv || exit $?

echo 'Computing deltas'
./compute_deltas.py || exit $?

#echo 'Deploying to S3'
#./deploy_data.py $ENVIRONMENT  || exit $?
#./deploy_lookups.py $ENVIRONMENT || exit $?
#./update_state_list.py $ENVIRONMENT $STATE_NAME CLEAR || exit $?
#./make_state_public.py $ENVIRONMENT $STATE_NAME || exit $?

