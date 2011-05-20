#!/usr/bin/env python

import re
import sys

from csvkit.unicsv import UnicodeCSVReader
from pymongo import Connection

import config

if len(sys.argv) < 2:
    sys.exit('You must provide the filename of a CSV as an argument to this script.')

FILENAME = sys.argv[1]

YEAR = '2010'

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.LABELS_COLLECTION]

with open(FILENAME) as f:
    rows = UnicodeCSVReader(f)
    headers = rows.next()

    inserts = 0
    row_count = 0

    table = None 
    hierarchy = []
    last_key = ''
    last_indent = 0

    for row in rows:
        row_count += 1

        text, key, table_id = row

        if not key.strip():
            # Skip empty spacer lines
            if not text.strip():
                continue
            
            # Table name row
            if re.match('^[A-Z]+[0-9]+.\s+', text):
                # Save previous table
                if table:
                    collection.save(table)

                match = re.match('^([A-Z]+[0-9]+).\s+(.*?)\s+\[([0-9]+)\]', text)

                table = {
                    'name': match.group(2),
                    'key': match.group(1),
                    'year': '2010', 
                    'size': int(match.group(3)),
                    'universe': '',
                    'labels': {}
                }
                
                # Remove existing table
                collection.remove({ 'key': table['key'], 'year': table['year'] })

                hierarchy = []
                last_key = ''
                last_indent = 0

                continue

            # Universe definition
            if text.startswith('Universe'):
                match = re.match('^Universe:\s+(.*)', text)

                table['universe'] = match.group(1) 

                continue

        whitespace_count = 0

        while text[whitespace_count] == ' ':
            whitespace_count += 1

        # Census uses 2-space indents to denote hierarchy
        indent = whitespace_count / 2

        if indent > last_indent:
            hierarchy.append((last_key, last_indent))

        while indent < last_indent:
            hierarchy.pop()
            last_indent = hierarchy[-1][1]

        if hierarchy:
            parent = hierarchy[-1][0]
        else:
            parent = None

        table['labels'][key] = {
            'text': text.strip().strip(':'),
            'indent': indent,
            'parent': parent
        }

        inserts += 1

        last_key = key
        last_indent = indent

    # Save final table
    collection.save(table)

print 'Row count: %i' % row_count
print 'Inserted: %i' % inserts

