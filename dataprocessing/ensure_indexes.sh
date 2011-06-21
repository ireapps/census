#!/bin/bash

echo "use census; 
db.geographies.ensureIndex({ 'geoid': 1 });
db.geographies.ensureIndex({ 'xrefs.FILEID': 1, 'xrefs.STUSAB': 1, 'xrefs.LOGRECNO': 1 });
db.geographies.ensureIndex({ 'metadata.NAME': 1 });
db.geographies_2000.ensureIndex({ 'xrefs.FILEID': 1, 'xrefs.STUSAB': 1, 'xrefs.LOGRECNO': 1 });" | mongo
