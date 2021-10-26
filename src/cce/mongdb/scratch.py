from pymongo import MongoClient
from rich import print
client = MongoClient('mongodb://localhost:27017/')
print(client.list_database_names())