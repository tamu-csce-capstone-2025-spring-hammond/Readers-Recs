# backend/database.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os


def open_connection():
    load_dotenv(override=True)
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI is not set")

    client = MongoClient(uri, server_api=ServerApi("1"))
    return client


def close_connection(client):
    client.close()
