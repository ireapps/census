#!/bin/bash

# NOTE: This script does absolutely everything, including download a whole gob of data. It exists mostly to document the correct order for running the scripts.

./fetch_data.sh

./load_pl_geographies_2000.py data/ilgeo2000.csv
./load_pl_data_2000.py data/il000012000.csv

# ./load_dpsf_geographies_2010.py data/rigeo2010.csv
# ./load_dpsf_data_2010.py data/ri000012010.csv
# ./load_dpsf_data_2000.py data/ri000012000.csv

./load_pl_geographies_2010.py data/ilgeo2010.csv

# Note: the crosswalk can be computed before the 2010 data is loaded
./load_crosswalk.py data/us2010trf.csv
./load_pl_data_2010.py data/il000012010.csv

./load_pl_labels_2010.py data/PL2010_Table.csv

./crosswalk.py
./compute_deltas.py
