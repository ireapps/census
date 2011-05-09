#!/usr/bin/env python

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config
import utils

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.LABELS_COLLECTION]

with open(config.PL_2010_LABELS_FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    row_count = 0

    for row in rows:
        row_count += 1

        text, key, table = row

        # Skip empty rows and table headers
        if not key.strip():
            continue

        whitespace = 0

        while text[whitespace] == ' ':
            whitespace += 1

        print whitespace


print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

