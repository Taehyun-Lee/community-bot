
from pymongo import MongoClient
from contextlib import contextmanager

@contextmanager
def use_mongodb(db_name, collection_name):
  client = MongoClient("localhost", 27017)
  db = client[db_name]
  collection = db[collection_name]
  try:
    yield collection
  finally:
    client.close()