from django.conf import settings
from pymongo import Connection

def get_labels_collection():
    connection = Connection()
    db = connection[settings.LABELS_DB] 
    return db[settings.LABELS_COLLECTION]

def get_labels_for_table(table):
    labels = get_labels_collection()
    dataset = labels.find_one({ 'dataset': 'SF1' }, fields=['tables'])

    return dataset['tables'][table]

def get_tables():
    labels = get_labels_collection()
    dataset = labels.find_one({ 'dataset': 'SF1' }, fields=['tables'])

    return sorted([x['key'] for x in dataset['tables']])
