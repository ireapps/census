#!/bin/bash
# somewhat redundant to patch_data.sh but I'm not great at factoring shell scripts...

MONGO_DUMP_DIR="/mnt/data/mongodumps"
ENVIRONMENT='production'
echo Begin redeploy at `date`

#!/bin/bash
if [ -z "$1" ]
then
  echo "Specify one or more state FIPS codes as arguments."
  exit
else
  WORK="$@"
fi

for STATE_FIPS in $WORK
do
    echo Begin $STATE_FIPS at `date`

    mongorestore -d census --drop ${MONGO_DUMP_DIR}/${STATE_FIPS}/census

    echo 'Deploying to S3'
    ./deploy_data.py $ENVIRONMENT public-read || exit $?
    ./deploy_lookups.py $ENVIRONMENT || exit $?
    ./deploy_labels.py $ENVIRONMENT || exit $?
    ./deploy_csv.py $STATE_FIPS 040 $ENVIRONMENT public-read || exit $?
    ./deploy_csv.py $STATE_FIPS 050 $ENVIRONMENT public-read || exit $?
    ./deploy_csv.py $STATE_FIPS 060 $ENVIRONMENT public-read || exit $?
    ./deploy_csv.py $STATE_FIPS 140 $ENVIRONMENT public-read || exit $?
    ./deploy_csv.py $STATE_FIPS 160 $ENVIRONMENT public-read || exit $?

    echo Complete $STATE_FIPS at `date`
done

echo Complete redeploy at `date`
