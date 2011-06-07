#!/bin/bash

# See batch.sh for notes.

./__drop_database.sh

./ensure_indexes.sh

./fetch_test_data.sh

./load_pl_geographies_2000.py data/degeo2000.csv
./load_pl_data_2000.py data/pl_data_2000_delaware_1.csv
./load_pl_data_2000.py data/pl_data_2000_delaware_2.csv

./load_pl_geographies_2010.py data/degeo2010.csv

./load_crosswalk.py 10 data/us2010trf.csv
./load_pl_data_2010.py data/pl_data_2010_delaware_1.csv
./load_pl_data_2010.py data/pl_data_2010_delaware_2.csv

./load_pl_labels_2010.py data/pl_2010_data_labels.csv

./crosswalk.py 10
./compute_deltas_pl.py 10

./deploy_data.py
./deploy_lookups.py
./update_state_list.py Delaware CLEAR

./tests.py
