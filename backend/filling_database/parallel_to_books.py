import re
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import requests as req
import os


client = MongoClient("<ADD AUTH HERE>")
db = client["Readers-Recs"]
books_collection = db["Books"]
parallel_collection = db["Parallel-Books"]
print("✅ Connected to MongoDB successfully!")

for parallel_book in parallel_collection.find():
    isbn13 = parallel_book.get("isbn13")
    if not isbn13:
        continue

    existing_book = books_collection.find_one({"isbn13": isbn13})
    if existing_book:
        print(f"ISBN13: {isbn13} already exists")
        continue

    copy = parallel_book
    copy.pop("_id", None)

    result = books_collection.insert_one(copy)
    print(f"Inserted new book with ISBN13: {isbn13}, bookid={result.inserted_id}.")
