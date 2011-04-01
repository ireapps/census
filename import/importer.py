#!/usr/bin/env python
import psycopg2
import argparse 
import csv
from os import listdir
DB_CONNECT_STRING = "dbname=censusweb user=censusweb"

import argparse

INSERT_SQL = "insert into tract_data(%s) values (%s)"
CREATE_SQL = "create table tract_data (%s)"

def parse_args():
    parser = argparse.ArgumentParser(description='Load raw census data that has already been downloaded.')
    parser.add_argument('-c','--clear', dest='clear', action='store_true',
                        help='Clear all existing data.')
    parser.add_argument('--createdb', dest='create_db', action='store_true',
                        help='Create the database.')

    return parser.parse_args()

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



def load_file(file_name,init_tables):
    reader = csv.reader(open(file_name), delimiter='\t')
    header = reader.next()
    if init_tables:
        create_tables(cur,header)
    for line in reader:
        INSERT_SQL % (", ".join(header), ", ".join(line))
        
if __name__ == '__main__':
    
    for i, file in enumerate(listdir("./data")):
        load_file(file,not bool(i))
    
    file = csv.reader(open('data/Mississippi.tsv'), delimiter='\t')
    first_line = file.next()
    
    # Connect to a database
    conn = psycopg2.connect(DB_CONNECT_STRING)
    cur = conn.cursor()
    create_tables(cur)
    conn.commit()
    
    cur.close()
    conn.close()
    