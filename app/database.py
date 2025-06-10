
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        db_uri = os.getenv('MONGO_URI')
        client = MongoClient(db_uri, server_api=ServerApi('1'))
        db = client["vanlife_db"]
        print("connection succesful")
        return db
    except Exception as e:
        print(e)
        return None


