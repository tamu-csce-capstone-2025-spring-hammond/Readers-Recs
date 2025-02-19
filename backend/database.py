from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

uri = os.getenv("MONGO_URI")
if not uri:
    raise ValueError("MONGO_URI is not set")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client["Readers-Recs"]

collections = {
    "Books": db["Books"],
    "Chat_Messages": db["Chat_Messages"],
    "Comments": db["Comments"],
    "Posts": db["Posts"],
    "User_Bookshelf": db["User_Bookshelf"],
    "Users": db["Users"]
}
