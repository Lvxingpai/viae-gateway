from pymongo import MongoClient

from app.local_settings import MONGO_URL

client = MongoClient(MONGO_URL)