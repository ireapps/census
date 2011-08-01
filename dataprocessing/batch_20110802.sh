#!/bin/bash
# 17 IL 
./batch_sf.sh "Illinois" production
./deploy_data.py staging 
./deploy_lookups.py staging 
./deploy_labels.py staging 
# 46 SD 
./batch_sf.sh "South Dakota" production
# 32 NV 
./batch_sf.sh "Nevada" production
# 41 OR 
./batch_sf.sh "Oregon" production
# 18 IN 
./batch_sf.sh "Indiana" production
# 53 WA 
./batch_sf.sh "Washington" production
