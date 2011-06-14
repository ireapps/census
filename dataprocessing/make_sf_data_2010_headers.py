#!/usr/bin/env python

import csv
import re
import sys

TABLE_REGEX = re.compile('([A-Z]+)([0-9]+)([A-Z]?)')

FIXED_HEADERS = ['FILEID', 'STUSAB', 'CHARITER', 'CIFSN', 'LOGRECNO']

# Values are tuples of (first table in file, total number of data cells in file)
# The latter is for a sanity check
FILES_TO_FIRST_TABLE_MAP = {
    1: ('P1', 1),
    2: ('P2', 6),
    3: ('P3', 194),
    4: ('P10', 239),
    5: ('P15', 245),
    6: ('P31', 254),
    7: ('P50', 251),
    8: ('P12F', 253),
    9: ('P17B', 249),
    10: ('P29A', 252),
    11: ('P31A', 254),
    12: ('P34F', 251),
    13: ('P38F', 240),
    14: ('P39I', 20),
    15: ('PCT1', 251),
    16: ('PCT9', 59),
    17: ('PCT12', 209),
    18: ('PCT13', 188),
    19: ('PCT21', 216),
    20: ('PCT12A', 209),
    21: ('PCT12B', 209),
    22: ('PCT12C', 209),
    23: ('PCT12D', 209),
    24: ('PCT12E', 209),
    25: ('PCT12F', 209),
    26: ('PCT12G', 209),
    27: ('PCT12H', 209),
    28: ('PCT12I', 209),
    29: ('PCT12J', 209),
    30: ('PCT12K', 209),
    31: ('PCT12L', 209),
    32: ('PCT12M', 209),
    33: ('PCT12N', 209),
    34: ('PCT12O', 209),
    35: ('PCT13A', 245),
    36: ('PCT13F', 245),
    37: ('PCT19C', 237),
    38: ('PCT20F', 254),
    39: ('PCT22G', 63),
    40: ('PCO1', 234),
    41: ('PCO7', 156),
    42: ('H1', 1),
    43: ('H2', 6),
    44: ('H3', 249),
    45: ('H11G', 255),
    46: ('H17D', 126),
    47: ('HCT1', 74)
}

FIELD_INDEX = sys.argv[1]

current_file = 1
headers = []

with open(FIELD_INDEX, 'r') as f:
    rows = csv.reader(f)

    # burn headers
    rows.next()
    rows.next()
    rows.next()
    
    for row in rows:
        table_name = row[0]
        field_num = row[1]

        # Skip table header rows
        if not field_num or field_num.startswith('POPULATION SUBJECTS') or field_num.startswith('HOUSING SUBJECTS'):
            continue

        # Final table contains all remaining
        if current_file != 47:
            # Have we switched files?
            if table_name.strip('.') == FILES_TO_FIRST_TABLE_MAP[current_file + 1][0]:
                if len(headers) != FILES_TO_FIRST_TABLE_MAP[current_file][1]:
                    raise AssertionError('Only found %i/%i headers for file %i' % (len(headers), FILES_TO_FIRST_TABLE_MAP[current_file + 1][1], current_file))

                with open('sf_data_2010_headers_%i.csv' % current_file, 'w') as f:
                    f.write(','.join(FIXED_HEADERS))
                    f.write(',')
                    f.write(','.join(headers))
                    f.write('\n')
                
                current_file += 1
                headers = []

                print 'Switched to file %i at table %s' % (current_file, table_name)
        
        parts = TABLE_REGEX.match(table_name)

        key = parts.group(1)
        key += parts.group(2).rjust(3, '0')
        
        if parts.group(3):
            key += parts.group(3)

        key += field_num.rjust(3, '0')

        headers.append(key)

    # Write final file
    with open('sf_data_2010_headers_%i.csv' % current_file, 'w') as f:
        f.write(','.join(FIXED_HEADERS))
        f.write(',')
        f.write(','.join(headers))
        f.write('\n')

