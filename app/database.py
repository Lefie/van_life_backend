from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        db_uri = os.getenv('MONGO_URI')
        client = MongoClient(db_uri, server_api=ServerApi('1'))
        client.admin.command("ping")
        print("connection succesful")
        return client
    except Exception as e:
        print(e)
        return None


