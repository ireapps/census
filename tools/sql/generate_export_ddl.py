#!/usr/bin/env python
"""
Generate SQL "Create table" files for all of the SF1 tables, with column format compatible with
the bulk download files available at http://census.ire.org/data/bulkdata.html

Note that all table names and column names will be forced to lowercase for maximum interoperability
between databases.
"""
from sqlalchemy import Column, MetaData, Table
from sqlalchemy import Float, Integer, String
from sqlalchemy.schema import CreateTable

import json

import os.path
import sys

LABELS = json.load(open("../metadata/sf1_labels.json"))

def _create_base_table(name):
    """Provide the common columns for all of our exports"""
    metadata = MetaData()
    sql_table = Table(name.lower(), metadata)
    sql_table.append_column(Column('geoid', String(length=11), primary_key=True))
    sql_table.append_column(Column('sumlev', String(length=3), nullable=False))
    sql_table.append_column(Column('state', String(length=2), nullable=False))
    sql_table.append_column(Column('county', String(length=3)))
    sql_table.append_column(Column('cbsa', String(length=5)))
    sql_table.append_column(Column('csa', String(length=3)))
    sql_table.append_column(Column('necta', String(length=5)))
    sql_table.append_column(Column('cnecta', String(length=3)))
    sql_table.append_column(Column('name', String(length=90), nullable=False))
    sql_table.append_column(Column('pop100', Integer, nullable=False))
    sql_table.append_column(Column('hu100', Integer, nullable=False))
    sql_table.append_column(Column('pop100_2000', Integer, nullable=True))
    sql_table.append_column(Column('hu100_2000', Integer, nullable=True))
    return sql_table

def sqlalchemy_for_table(table_code,table_name_prefix='ire_'):
    table_labels = LABELS[table_code]
    if table_labels['name'].find('AVERAGE') != -1 or table_labels['name'].find('MEDIAN') != -1:
        col_type = Float
    else:
        col_type = Integer
    sql_table = _create_base_table("%s%s" % (table_name_prefix,table_code))    
    for label in sorted(table_labels['labels']):
        sql_table.append_column(Column(label.lower(), col_type))
        sql_table.append_column(Column("%s_2000" % label.lower(), col_type))
    return sql_table

def sql_for_table(table_code,table_name_prefix='ire_'):
    sql_table = sqlalchemy_for_table(table_code,table_name_prefix)
    return unicode(CreateTable(sql_table).compile(dialect=None)).strip()

if __name__ == "__main__":
    try:
        output_dir = sys.argv[1]
    except:
        output_dir = '.'

    table_name_prefix = 'ire_'

    for table_code in sorted(LABELS):
        table_name = LABELS[table_code]['name']
        fn = os.path.join(output_dir,"%s%s.sql" % (table_name_prefix,table_code))
        with open(fn,"w") as f:
            f.write("-- %s. %s\n" % (table_code,table_name))
            f.write("-- designed to work with the IRE Census bulk data exports\n")
            f.write("-- see http://census.ire.org/data/bulkdata.html\n")
            f.write(sql_for_table(table_code))
            f.write(';\n')
