#!/usr/bin/env python
import psycopg2
import csv
import urllib
from os import listdir
import os.path

class CrosswalkImporter:
    def __init__(self, geo_level="tract"):
        DB_CONNECT_STRING = "dbname=censusweb user=censusweb"
        self.conn = psycopg2.connect(DB_CONNECT_STRING)
        self.cur = self.conn.cursor()
            
    def fetch_crosswalk(self):
        urllib.urlretrieve ("http://www.census.gov/geo/www/2010census/tract_rel/trf_txt/us2010trf.txt", "./data/cross.txt")
        
    def import_crosswalk(self):
        self.cur.execute("drop table if exists crosswalk")
        self.conn.commit()
        self.cur.execute("create table crosswalk (STATE00 varchar(255),COUNTY00 varchar(255),TRACT00 varchar(255),GEOID00 varchar(255),STATE10 varchar(255),COUNTY10 varchar(255),TRACT10 varchar(255),GEOID10 varchar(255),AREALANDPCT00PT numeric(5,2),AREALANDPCT10PT numeric(5,2))")
        reader = csv.reader(open(os.path.join("./data","cross.txt")), delimiter=',')
        for line in reader:
            sql = "insert into crosswalk (STATE00,COUNTY00,TRACT00,GEOID00,STATE10,COUNTY10,TRACT10,GEOID10,AREALANDPCT00PT,AREALANDPCT10PT) values ('%s','%s','%s','%s','%s','%s','%s','%s',%s,%s)" %  (line[0],line[1],line[2],line[3],line[9],line[10],line[11],line[12],line[21],line[23])
            self.cur.execute(sql)
            self.conn.commit()