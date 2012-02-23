#!/usr/bin/env bash
TABLE=$1
STATE=$2
SUMLEV=$3
LOWER_TABLE=`echo $TABLE | tr '[A-Z]' '[a-z]'`

DATABASE='nicar'
echo table $TABLE state $STATE sumlev $SUMLEV
curl https://raw.github.com/ireapps/census/master/tools/sql/ire_export/ire_${TABLE}.sql | psql $DATABASE
curl http://censusdata.ire.org/${STATE}/all_${SUMLEV}_in_${STATE}.${TABLE}.csv | gzcat > all_${SUMLEV}_in_${STATE}.${TABLE}.csv
psql -c "copy ire_${LOWER_TABLE} from '/Users/germuska/src/all_${SUMLEV}_in_${STATE}.${TABLE}.csv' csv header" ${DATABASE}