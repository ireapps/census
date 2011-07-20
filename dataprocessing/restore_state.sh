#!/bin/bash
# Given a state fips code, restore that state to the mongo DB
# this REPLACES current data, so use with caution
MONGO_DUMP_DIR="/mnt/data/mongodumps"
STATE_FIPS="${@:1:1}"

mongorestore -d census --drop ${MONGO_DUMP_DIR}/${STATE_FIPS}/census