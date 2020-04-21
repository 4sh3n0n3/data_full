from data_prod.settings import MONGO_CONNECTION
from pymongo import MongoClient


def _get_database():
    client = MongoClient(MONGO_CONNECTION.get('host'), MONGO_CONNECTION.get('port'))
    return client[MONGO_CONNECTION.get('db_name')]


def insert_data(data, collection):
    return _get_database()[collection].insert_many(data).inserted_ids


def find_data(collection, limit=0, skip=0, filter_json=None, projection=None):
    return _get_database()[collection].find(filter=filter_json, projection=projection).skip(skip).limit(limit)


def count_data(collection, filter_json=None):
    return _get_database()[collection].count(filter=filter_json)
