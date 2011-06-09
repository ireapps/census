from django.conf import settings

from pymongo import Connection

def get_labels_collection():
    connection = Connection()
    db = connection[settings.LABELS_DB] 
    return db[settings.LABELS_COLLECTION]

def get_labelset():
    labels = get_labels_collection()
    labelset = labels.find_one({ 'dataset': settings.DATASET })

    return labelset

