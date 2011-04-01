#!/usr/bin/env python
import psycopg2

import csv
from os import listdir
import os.path
from lib import STATES
import re

STATE_NUMBERS = dict((x[0],x[1]) for x in STATES)

DB_CONNECT_STRING = "dbname=censusweb user=censusweb"

import argparse

INSERT_SQL = "insert into tract_data(%s) values (%s)"
CREATE_SQL = "create table tract_data (%s)"


def clear_database():
    pass

def create_database():
    pass

def create_tables(cur, first_line):
    def tablize(q):
        return q.replace(" ", "_") + ' VARCHAR(255)'
    fields = map(tablize, first_line)
    line = CREATE_SQL % ", ".join(fields)
    cur.execute(line)
        
def do_the_db():
    # Execute a command: this creates a new table
    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database



def load_file(cur,file_name,init_tables):
    reader = csv.reader(open(file_name), delimiter='\t')
    header = reader.next()
    if init_tables:
        create_tables(cur,header)
        
    match = re.findall('(\d+)\.tsv',file_name)
    cur.execute("delete from tract_data where state_fips = %s",(match[0],))    
    columns = ", ".join(map(lambda x: x.replace(' ','_'),header))    
    for i,line in enumerate(reader):
        sql = INSERT_SQL % (columns, ", ".join(map(lambda x: "'%s'" % x,line)))
        cur.execute(sql)
        
    print "done: %s" % file_name    
if __name__ == '__main__':
    
    # Connect to a database
    conn = psycopg2.connect(DB_CONNECT_STRING)
    cur = conn.cursor()

    cur.execute("drop table if exists tract_data")

    for i, file in enumerate(listdir("./data")):
        load_file(cur,os.path.join("./data",file),not bool(i))
    
    conn.commit()
    cur.close()
    conn.close()
    