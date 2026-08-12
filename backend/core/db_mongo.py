# core/db_mongo.py
from pymongo import MongoClient
import os

# It's better to pull from environment or settings, 
# but for now, we'll use your direct string.
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

client = MongoClient(MONGO_URL)
mongodb = client[DB_NAME]

# Now you can use 'mongodb' in any other file