#!/bin/bash

# NOTE: This script does absolutely everything, including download a whole gob of data. It exists mostly to document the correct order for running the scripts.

./fetch_data.sh

./load_geographies_2000.py
./load_pl_2000.py

./load_geographies_2010.py

./load_crosswalk.py
./load_pl_2010.py

./crosswalk.py
./compute_deltas.py
