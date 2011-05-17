#!/bin/bash

# See batch.sh for notes.

#echo "use census; 
#db.dropDatabase();" | mongo

./fetch_sf_data.sh

./load_sf_geographies_2000.py data/degeo2000.csv
./load_sf_data_2000.py data/sf_data_2000_delaware_1.csv

#./load_pl_labels_2010.py data/pl_2010_data_labels.csv
