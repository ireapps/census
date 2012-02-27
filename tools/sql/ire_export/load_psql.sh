#!/usr/bin/env bash
# usage: ./load_psql.sh [TABLE CODE] [STATE FIPS CODE] [SUMMARY LEVEL]
# supports all 331 Census 2010 tables
# only the five summary levels supported by the IRE Census app:
#   040 State
#   050 County
#   060 County Subdivision
#   140 Census Tract
#   160 Place
# see also http://census.ire.org/data/bulkdata.html
# list of FIPS state codes at http://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code#FIPS_state_codes

# change this to your default database, or tweak the script to make it a parameter
DATABASE='nicar'

TABLE=$1
STATE=$2
SUMLEV=$3
LOWER_TABLE=`echo $TABLE | tr '[A-Z]' '[a-z]'`

echo table $TABLE state $STATE sumlev $SUMLEV
curl https://raw.github.com/ireapps/census/master/tools/sql/ire_export/ire_${TABLE}.sql | psql $DATABASE
curl http://censusdata.ire.org/${STATE}/all_${SUMLEV}_in_${STATE}.${TABLE}.csv | gzcat > all_${SUMLEV}_in_${STATE}.${TABLE}.csv
psql -c "copy ire_${LOWER_TABLE} from '/Users/germuska/src/all_${SUMLEV}_in_${STATE}.${TABLE}.csv' csv header" ${DATABASE}