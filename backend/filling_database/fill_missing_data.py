import re
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import requests as req
import os

client = MongoClient("<ADD AUTH HERE>")
db = client["Readers-Recs"]
books_collection = db["Books"]
print("✅ Connected to MongoDB successfully!")

def findBooksMissingData(start=None):
    missing_data_filter = {
        "$or": [
            {"page_count": 0},
            {"summary": ""}
        ]
    }
    
    cursor = books_collection.find(missing_data_filter)
    
    #isbn_list = []
    isbn13_list = []
    count = 0

    for book in cursor:
        #
        if "isbn13" in book and book["isbn13"]:
            isbn13_list.append(book["isbn13"])
            count += 1
            
    if start and start in isbn13_list:
        startidx = isbn13_list.index(start)
        isbn13_list = isbn13_list[start:]
    
    print("Count:", count)
    print("ISBN13s missing data:", isbn13_list)

    return isbn13_list
    
def cleanSynopsisText(synopsis: str) -> str:
    cleaned = re.sub(r"<[^>]*>", " ", synopsis) 
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned

def addMissingData():
    isbn13_list = findBooksMissingData()
    
    for isbn13 in isbn13_list:
        h = {'Authorization': '<ADD AUTH HERE>'}
        url = f"https://api2.isbndb.com/book/{isbn13}"
        resp = req.get(url, headers=h)

        if resp.status_code == 200:
            response_data = resp.json()

            book_data = response_data.get("book", {})
            if book_data:
                
                synopsis = book_data.get("synopsis", "")
                page_count = book_data.get("pages", 0)
                
                cleaned_synopsis = cleanSynopsisText(synopsis)

                update_result = books_collection.update_one(
                    {"isbn13": isbn13},
                    {
                        "$set": {
                            "summary": cleaned_synopsis,
                            "page_count": page_count
                        }
                    }
                )
                print(f"Updated book {isbn13}: matched={update_result.matched_count}, modified={update_result.modified_count}")
            else:
                print(f"No 'book' field in response for {isbn13}:", response_data)
        else:
            print(f"Error fetching data for ISBN13: {isbn13}. Status code: {resp.status_code}")


if __name__ == '__main__':=
    addMissingData()