#!/usr/bin/env python

from pymongo import Connection, objectid 

from csvkit.unicsv import UnicodeCSVWriter

import sys
import re

import config

TABLE_CODE_PATTERN = re.compile('^(\D+)(\d+)(\D+)?$')

def compare_table_codes(a,b):
    a_type,a_number,a_subtype = TABLE_CODE_PATTERN.match(a).groups()
    b_type,b_number,b_subtype = TABLE_CODE_PATTERN.match(b).groups()
    a_number = int(a_number)
    b_number = int(b_number)
    if a_type != b_type:
        if a_type[0] != b_type[0]:
            return cmp(a_type[0],b_type[0]) * -1 # Sort P before H to match tech docs
        return cmp(a_type,b_type)
    if a_number != b_number:
        return cmp(a_number,b_number)
    return cmp(a_subtype,b_subtype)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('You must provide the filename for the CSV output as an argument to this script.')

    FILENAME = sys.argv[1]
    with open(FILENAME,"w") as f:
        connection = Connection()
        db = connection[config.LABELS_DB] 
        collection = db[config.LABELS_COLLECTION]

        labelset = collection.find_one({ 'dataset': 'SF1' })

        w = UnicodeCSVWriter(f)
        w.writerow(['table_code','table_desc','table_universe','table_size','col_code','col_desc','indent','parent','has_children','col_code_2000'])
        for table_code in sorted(labelset['tables'],cmp=compare_table_codes):
            t = labelset['tables'][table_code]
            row_base = [table_code,t['name'],t['universe'],t['size']]
            for label_code in sorted(t['labels']):
                l = t['labels'][label_code]
                row = row_base[:]
                if l['parent'] is None: parent = ''
                else: parent = l['parent']
                if l['key_2000'] is None: key_2000 = ''
                else: key_2000 = l['key_2000']
                row.extend([l['key'],l['text'],l['indent'],parent,l['has_children'],key_2000])
                w.writerow(row)
