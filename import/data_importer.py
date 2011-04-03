#!/usr/bin/env python
# from data_importer import DataImporter 
# 

import psycopg2
import csv
import urllib
from os import listdir
import os.path
from lib import STATES
import re

class DataImporter:
    def __init__(self, geo_level="tract"):
        DB_CONNECT_STRING = "dbname=censusweb user=censusweb"
        self.conn = psycopg2.connect(DB_CONNECT_STRING)
        self.cur = self.conn.cursor()
        self.table_name = geo_level + "_data_2000"
        self.files = filter(lambda x: x.endswith(".tsv"), listdir("./data"))
        
    def import_data(self):
        self._drop_old_tables()        
        fields_and_values = self.get_data_headers()
        self._create_tables(fields_and_values)
        self._insert_data(fields_and_values)
            
    def get_data_headers(self):
        data_and_headers = self._get_file_heads()
        fields_and_values = self._tablize_headers(data_and_headers)
        return fields_and_values
            
    #protected methods
    def _create_tables(self,fields_and_values):
        create_sql = "create table %s (%s)" % (self.table_name, ",".join(fields_and_values["fields"]))
        self.cur.execute(create_sql)
        self.conn.commit()
        
    def _insert_data(self,fields_and_values):
        insert_sql = "insert into " + self.table_name + " (" + ",".join(fields_and_values['headers']) + ")"
        for file in self.files:
            reader = csv.reader(open(os.path.join("./data",file)), delimiter='\t')
            header = reader.next()
            for i,line in enumerate(reader):
                values = ",".join(self._string_or_num(fields_and_values, line))
                self.cur.execute(insert_sql + " values (" + values + ")")
                self.conn.commit()
                print "Working on file %s" % file + "\t: Line %s" % str(i)
        
    def _string_or_num(self,fields_and_values,line):
        results = []
        for i,type in enumerate(fields_and_values["types"]):
            if type == "s":
                results.append("'" + line[i] + "'")
            else:
                results.append(line[i])
        return results
            
    def _get_file_heads(self):
        reader = csv.reader(open(os.path.join("./data", self.files[0])), delimiter='\t')
        header_line = reader.next()
        data_line = reader.next()
        return {"fields":[], "headers":header_line, "data_line":data_line, "types":[]}
            
    def _tablize_headers(self, data_and_headers):
        for i,node in enumerate(data_and_headers["data_line"]):
            header = data_and_headers["headers"][i].replace(" ", "_")
            data_and_headers["headers"][i] = header
            datatype = self._of_type(node, header)
            data_and_headers["fields"].append(header + datatype[1])
            data_and_headers["types"].append(datatype[0])
        return data_and_headers
       
    def _of_type(self,node,header):
        SPECIAL_HEADERS = ["Summary_Level", "Geographic_Component", "State_FIPS", "Place_FIPS", "County_FIPS", "Tract", "Zip", "Block", "Name"]
        if header in SPECIAL_HEADERS:
            return ("s"," VARCHAR(255)")
        elif re.search('^-?\d+\.\d+$', node):
            return ("n"," NUMERIC(11,6)")
        elif node.isdigit() and not re.search('^0', node):
            return ("i"," INTEGER")
        else:
            return ("s"," VARCHAR(255)")
            
    def _drop_old_tables(self):
        self.cur.execute("drop table if exists %s" % self.table_name)
        self.conn.commit()