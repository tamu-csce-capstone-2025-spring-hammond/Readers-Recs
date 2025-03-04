import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

def get_favorite_genres(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    genres_section = soup.find("div", class_="stacked clearFloats bigBox")
    if not genres_section:
        print("Genres section not found.")
        return []
    
    genres_div = genres_section.find("div", class_="bigBoxBody")
    if not genres_div:
        print("No genres found.")
        return []
    
    genres = [a.text.strip() for a in genres_div.find_all("a", href=True)]
    return genres

def get_rating(row):
    rating_div = row.find("td", class_="field rating")
    if not rating_div:
        return 0
    
    star_elements = rating_div.find_all("span", class_="staticStar p10")
    return len(star_elements)

def clean_isbn(text):
    return re.sub(r'[^0-9]', '', text)

def clean_isbn13(text):
    return re.sub(r'[^0-9]', '', text).lstrip('13')

def clean_title(title_field):
    if title_field:
        title_link = title_field.find("a")
        if title_link:
            return title_link.text.strip()
    return ""

def create_user(users_collection, favorite_genres):
    user_data = {
        "_id": str(ObjectId()), 
        "first_name": "user51",
        "last_name": "db",
        "username": "username51",
        "email_address": "user51@email.com",
        "interests": favorite_genres,
        "demographics": {
            "gender": "",
            "age": "",
            "country": "",
            "birthday": ""
        }
    }
    users_collection.insert_one(user_data)
    return user_data["_id"]

def find_book_in_db(books_collection, isbn13, isbn, title):
    book_entry = books_collection.find_one({"isbn13": isbn13})
    if not book_entry: 
        book_entry = books_collection.find_one({"isbn": isbn})
    if not book_entry:
        book_entry = books_collection.find_one({"title": {"$regex": title, "$options": "i"}})
    if not book_entry:
        if isinstance(title, str):
            regex_pattern = f"^.*{re.escape(title)}.*$"
            book_entry = books_collection.find_one({"title": {"$regex": regex_pattern, "$options": "i"}})
    
    return book_entry


def scrape_and_store():
    user_url = 'https://www.goodreads.com/user/show/129991917-ally-wendling' # main profile page
    book_urls = [ # book shelf pages of read currently reading and to read
        'https://www.goodreads.com/review/list/129991917?shelf=read',
        'https://www.goodreads.com/review/list/129991917?shelf=currently-reading',
        'https://www.goodreads.com/review/list/129991917?shelf=to-read'
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    
    favorite_genres = get_favorite_genres(user_url)
    
    # Connect to MongoDB
    client = MongoClient("<Add client here>")
    db = client["Readers-Recs"]
    books_collection = db["Books"]
    users_collection = db["Users"]
    shelf_collection = db["User_Bookshelf"]
    
    user_id = create_user(users_collection, favorite_genres)
    
    i = 0
    count = 0
    for book_url in book_urls:
        if (i == 0):
            status = "read"
        elif (i == 1):
            status = "currently-reading"
        elif (i == 2):
            status = "to-read"
        i += 1
        response = requests.get(book_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        books_body = soup.find('tbody', id='booksBody')
        
        if not books_body:
            print(f"No books found at {book_url}.")
            continue

        rows = books_body.find_all('tr')

        for row in rows:
            isbn_field = row.find('td', class_='field isbn')
            isbn13_field = row.find('td', class_='field isbn13')
            title_field = row.find('td', class_='field title')
            
            if isbn_field and isbn13_field and title_field:
                isbn_value = clean_isbn(isbn_field.text.strip())
                isbn13_value = clean_isbn13(isbn13_field.text.strip())
                title_value = clean_title(title_field)
                #print(title_value)
                print(isbn13_value)
                book_entry = find_book_in_db(books_collection, isbn13_value, isbn_value, title_value)
                
                
                book_id = book_entry["_id"] if book_entry else None
                #print(book_id)
                if (book_id == None):
                    continue
                
                rating = get_rating(row)
                if (rating == 0):
                    rating = ""
                elif (rating > 3):
                    rating = "pos"
                elif (rating == 3):
                    rating = "mid"
                else:
                    rating = "neg"
                
                shelf_data = {
                    "_id": str(ObjectId()),
                    "user_id": user_id,
                    "book_id": book_id,
                    "status": status,
                    "rating": rating
                }
                
                shelf_collection.insert_one(shelf_data)
                count += 1
                
                print(f"Inserted/Updated: {shelf_data}")
            else:
                print("ISBN data not found")
    
    print("Scraping and storing complete.")
    print(count)

if __name__ == '__main__':
    scrape_and_store()