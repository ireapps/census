#!/usr/bin/env python
import psycopg2
import argparse 
DB_CONNECT_STRING = "dbname=censusweb user=censusweb"

import argparse

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
        
def do_the_db():
    # Connect to a database
    conn = psycopg2.connect(DB_CONNECT_STRING)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()
    
if __name__ == '__main__':
    args = parse_args()
    if args.create_db:
        create_database()
    elif args.rese
    if args.clear:
        clear_database()
        