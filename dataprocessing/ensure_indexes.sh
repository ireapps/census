#!/bin/bash

echo "use census; 
db.geographies.ensureIndex({ 'geoid': 1 });
db.geographies.ensureIndex({ 'xrefs': 1 });
db.geographies.ensureIndex({ 'metadata.NAME': 1 });
db.geographies_2000.ensureIndex({ 'geoid': 1 });" | mongo
