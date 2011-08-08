#!/bin/bash
# written originally to address mismapping of 2000 value for P004003 but should 
# probably be usable for other similar cases. 

MONGO_DUMP_DIR="/mnt/data/mongodumps"
echo Begin patching at `date`

#!/bin/bash
if [ -z "$1" ]
then
  WORK=`ls $MONGO_DUMP_DIR`
else
  WORK="$@"
fi

for STATE_FIPS in $WORK
do
    echo Begin $STATE_FIPS at `date`

    mongorestore -d census --drop $MONGO_DUMP_DIR/${STATE_FIPS}

    # if necessary, a script could be added here to make a patch; for the original case,
    # the fix was in a config file for crosswalk.py and no other processing needed to be done.

    echo 'Processing crosswalk'
    ./crosswalk.py || exit $?

    echo 'Computing deltas'
    ./compute_deltas_sf.py || exit $?

    echo 'Dumping mongo data for ${STATE_FIPS}'
    mkdir -p $MONGO_DUMP_DIR/${STATE_FIPS}
    mongodump -d census -o $MONGO_DUMP_DIR/${STATE_FIPS}

    echo 'Deploying to S3'
    ./deploy_data.py $ENVIRONMENT public || exit $?
# lookups and labels didn't change in this case...
#    ./deploy_lookups.py $ENVIRONMENT || exit $?
#    ./deploy_labels.py $ENVIRONMENT || exit $?
    ./deploy_csv.py $STATE_FIPS 040 $ENVIRONMENT public || exit $?
    ./deploy_csv.py $STATE_FIPS 050 $ENVIRONMENT public || exit $?
    ./deploy_csv.py $STATE_FIPS 060 $ENVIRONMENT public || exit $?
    ./deploy_csv.py $STATE_FIPS 140 $ENVIRONMENT public || exit $?
    ./deploy_csv.py $STATE_FIPS 160 $ENVIRONMENT public || exit $?

    echo Complete $STATE_FIPS at `date`
done

echo Complete patching at `date`
