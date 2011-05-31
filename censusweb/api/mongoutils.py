from django.conf import settings
from pymongo import Connection, ASCENDING

from constants import *

def get_geographies_collection():
    connection = Connection()
    db = connection[settings.CENSUS_DB] 
    return db[settings.GEOGRAPHIES_COLLECTION]

def get_labels_collection():
    connection = Connection()
    db = connection[settings.CENSUS_DB] 
    return db[settings.LABELS_COLLECTION]

def get_labels_for_table(year, table):
    labels = get_labels_collection()

    return labels.find_one({ 'year': year, 'key': table })

def get_tables_for_year(year):
    labels = get_labels_collection()

    return sorted([x['key'] for x in labels.find({'year' : '2010' },fields=['key'])])
