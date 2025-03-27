# backend/userbookshelf_data/script.py
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests as req
from bson.objectid import ObjectId
import sys
import requests
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import re


def parseinput(csv_string: str):
    parts = [p.strip() for p in csv_string.split(",")]
    if len(parts) < 4:
        raise ValueError("Input string must have at least 4 comma-separated values.")
    user_url = parts[0]
    gender = parts[1]
    age = parts[2]
    shelf_url = parts[3]
    return user_url, gender, age, shelf_url


def get_favorite_genres(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

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
    return re.sub(r"[^0-9]", "", text)


def clean_isbn13(text):
    return re.sub(r"[^0-9]", "", text).lstrip("13")


def clean_title(title_field):
    if title_field:
        title_link = title_field.find("a")
        if title_link:
            return title_link.text.strip()
    return ""


def create_user(users_collection, favorite_genres, i, g, a):
    user_data = {
        "_id": str(ObjectId()),
        "first_name": f"user{i}",
        "last_name": "db",
        "username": f"username{i}",
        "email_address": f"user{i}@email.com",
        "interests": favorite_genres,
        "demographics": {"gender": g, "age": a, "country": "", "birthday": ""},
        "embedding": [],
        "genre_weights": [],
    }
    users_collection.insert_one(user_data)
    return user_data["_id"]


def find_book_in_db(books_collection, isbn13, isbn, title):
    book_entry = books_collection.find_one({"isbn13": isbn13})
    if not book_entry:
        book_entry = books_collection.find_one({"isbn": isbn})
    if not book_entry:
        book_entry = books_collection.find_one(
            {"title": {"$regex": title, "$options": "i"}}
        )
    if not book_entry:
        if isinstance(title, str):
            regex_pattern = f"^.*{re.escape(title)}.*$"
            book_entry = books_collection.find_one(
                {"title": {"$regex": regex_pattern, "$options": "i"}}
            )

    return book_entry


def add_book_to_db(books_collection, isbn):
    existing_book = books_collection.find_one(
        {"$or": [{"isbn": isbn}, {"isbn13": isbn}]}
    )
    if existing_book:
        return existing_book

    class PyObjectId(ObjectId):
        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid objectid")
            return ObjectId(v)

    class BookSchema(BaseModel):
        id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
        author: List[str] = Field(default_factory=list)
        title: str = Field(default="")
        page_count: int = Field(default=0)
        genre: str = Field(default="")
        publication_date: datetime = Field(default_factory=datetime.now)
        isbn: str = Field(default="")
        isbn13: str = Field(default="")
        cover_image: str = Field(default="")
        language: str = Field(default="eng")
        publisher: str = Field(default="")
        tags: List[str] = Field(default_factory=list)
        summary: str = Field(default="")
        genre_tags: List[str] = Field(default_factory=list)
        embedding: List[float] = Field(default_factory=list)

        class Config:
            allow_population_by_field_name = True

    def get_book_data_google(isbn_value: str) -> dict:
        GOOGLE_BOOKS_API_KEY = "ADD KEY HERE"
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_value}&key={GOOGLE_BOOKS_API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "items" in data and data["items"]:
                    volume_info = data["items"][0].get("volumeInfo", {})
                    return {
                        "title": volume_info.get("title"),
                        "author": volume_info.get("authors", []),
                        "publisher": volume_info.get("publisher"),
                        "publication_date": volume_info.get("publishedDate"),
                        "page_count": volume_info.get("pageCount"),
                        "language": volume_info.get("language"),
                        "genre": volume_info.get("categories", [None])[0],
                        "cover_image": volume_info.get("imageLinks", {}).get(
                            "thumbnail"
                        ),
                        "summary": volume_info.get("description"),
                    }
        except Exception as e:
            print(f"❌ Google Books API error: {e}")
        return {}

    def get_book_data_openlibrary(isbn_value: str) -> dict:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_value}&format=json&jscmd=data"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                key = f"ISBN:{isbn_value}"
                if key in data:
                    book = data[key]
                    description = book.get("description", "")
                    if isinstance(description, dict):
                        description = description.get("value", "")
                    authors = [
                        a.get("name") for a in book.get("authors", []) if a.get("name")
                    ]
                    tags = [
                        subject.get("name")
                        for subject in book.get("subjects", [])
                        if subject.get("name")
                    ]
                    return {
                        "title": book.get("title"),
                        "author": authors,
                        "publisher": (
                            book.get("publishers", [{}])[0].get("name")
                            if book.get("publishers")
                            else None
                        ),
                        "publication_date": book.get("publish_date"),
                        "page_count": book.get("number_of_pages"),
                        "cover_image": book.get("cover", {}).get("medium"),
                        "summary": description,
                        "tags": tags,
                    }
        except Exception as e:
            print(f"❌ Open Library API error: {e}")
        return {}

    def parse_date(date_str: Optional[str]) -> datetime:
        if not date_str:
            return datetime.now()
        for fmt in ("%Y-%m-%d", "%Y"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return datetime.now()

    existing_book = books_collection.find_one(
        {"$or": [{"isbn": isbn}, {"isbn13": isbn}]}
    )
    if existing_book:
        return existing_book

    print(f"Book with ISBN '{isbn}' not found, querying external APIs...")
    google_data = get_book_data_google(isbn)
    openlib_data = get_book_data_openlibrary(isbn)

    title = google_data.get("title") or openlib_data.get("title") or "Unknown Title"
    authors = google_data.get("author") or openlib_data.get("author") or []
    publisher = (
        google_data.get("publisher")
        or openlib_data.get("publisher")
        or "Unknown Publisher"
    )
    pub_date_str = google_data.get("publication_date") or openlib_data.get(
        "publication_date"
    )
    publication_date = parse_date(pub_date_str)
    page_count = google_data.get("page_count") or openlib_data.get("page_count") or 0
    language = google_data.get("language") or "eng"
    genre = google_data.get("genre") or "Unknown Genre"
    cover_image = (
        google_data.get("cover_image")
        or openlib_data.get("cover_image")
        or "default_cover_image.jpg"
    )
    summary = google_data.get("summary") or openlib_data.get("summary") or ""
    tags = openlib_data.get("tags") or []

    if page_count == 0 or summary == "":
        addMissingData(isbn)

    try:
        new_book = BookSchema(
            isbn=isbn,
            isbn13=isbn,
            title=title,
            author=authors,
            publisher=publisher,
            publication_date=publication_date,
            page_count=page_count,
            language=language,
            genre=genre,
            cover_image=cover_image,
            summary=summary,
            tags=tags,
        )
    except ValidationError as ve:
        print("Validation error creating book schema:", ve)
        return None

    result = books_collection.insert_one(new_book.dict(by_alias=True))
    if result.inserted_id:
        print(
            f"✅ Book with ISBN '{isbn}' added successfully with _id: {result.inserted_id}"
        )
        return books_collection.find_one({"_id": result.inserted_id})
    else:
        print("❌ An error occurred while inserting the book.")
        return None


def cleanSynopsisText(synopsis: str) -> str:
    cleaned = re.sub(r"<[^>]*>", " ", synopsis)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def addMissingData(isbn13):
    h = {"Authorization": "<ADD AUTH HERE>"}
    url = f"https://api2.isbndb.com/book/{isbn13}"
    resp = req.get(url, headers=h)
    client = MongoClient("<ADD AUTH HERE>")
    db = client["Readers-Recs"]
    books_collection = db["Books"]

    if resp.status_code == 200:
        response_data = resp.json()

        book_data = response_data.get("book", {})
        if book_data:

            synopsis = book_data.get("synopsis", "")
            page_count = book_data.get("pages", 0)

            cleaned_synopsis = cleanSynopsisText(synopsis)

            update_result = books_collection.update_one(
                {"isbn13": isbn13},
                {"$set": {"summary": cleaned_synopsis, "page_count": page_count}},
            )
            print(
                f"Updated book {isbn13}: matched={update_result.matched_count}, modified={update_result.modified_count}"
            )
        else:
            print(f"No 'book' field in response for {isbn13}:", response_data)
    else:
        print(
            f"Error fetching data for ISBN13: {isbn13}. Status code: {resp.status_code}"
        )


def scrape_and_store(filepath: str, start_index: int):
    client = MongoClient("<ADD AUTH HERE>")
    db = client["Readers-Recs"]
    books_collection = db["Books"]
    users_collection = db["Users"]
    shelf_collection = db["User_Bookshelf"]

    current_index = start_index

    with open(filepath, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        user_url, gender, age, shelf_base_url = parseinput(line)
        favorite_genres = get_favorite_genres(user_url)

        user_id = create_user(
            users_collection, favorite_genres, current_index, gender, age
        )

        book_urls = [
            f"{shelf_base_url}?shelf=read",
            f"{shelf_base_url}?shelf=currently-reading",
            f"{shelf_base_url}?shelf=to-read",
        ]

        total_count = 0
        for book_url in book_urls:
            if total_count > 20:
                break

            print(f"Scraping shelf: {book_url}")

            status_match = re.search(r"shelf=([^&]+)", book_url)
            if status_match:
                status = status_match.group(1)
            else:
                status = "read"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            }

            resp = requests.get(book_url, headers=headers)
            if resp.status_code != 200:
                print(f"Error fetching shelf: {book_url}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            books_body = soup.find("tbody", id="booksBody")
            if not books_body:
                print(f"No books found at {book_url}.")
                continue

            rows = books_body.find_all("tr")
            shelf_count = 0

            for row in rows:
                isbn_field = row.find("td", class_="field isbn")
                isbn13_field = row.find("td", class_="field isbn13")
                title_field = row.find("td", class_="field title")

                if not (isbn_field and isbn13_field and title_field):
                    print("ISBN data not found on this row.")
                    continue

                isbn_val = clean_isbn(isbn_field.text.strip())
                isbn13_val = clean_isbn13(isbn13_field.text.strip())
                title_val = clean_title(title_field)

                if not isbn_val and not isbn13_val:
                    print("No valid ISBN.")
                    continue

                book_entry = find_book_in_db(
                    books_collection, isbn13_val, isbn_val, title_val
                )
                if not book_entry:
                    search_isbn = isbn13_val if isbn13_val else isbn_val
                    book_entry = add_book_to_db(books_collection, search_isbn)
                    if not book_entry:
                        print("Could not find or add the book.")
                        continue

                rating = get_rating(row)
                if rating == 0:
                    rating_str = ""
                elif rating > 3:
                    rating_str = "pos"
                elif rating == 3:
                    rating_str = "mid"
                else:
                    rating_str = "neg"

                bookshelfobj = {
                    "_id": str(ObjectId()),
                    "user_id": user_id,
                    "book_id": book_entry["_id"],
                    "status": status,
                    "rating": rating_str,
                }
                shelf_collection.insert_one(bookshelfobj)
                shelf_count += 1

                print(f"Inserted/Updated bookshelf entry: {bookshelfobj}")

            total_count += shelf_count
            print(f"{shelf_count} records inserted/updated for shelf '{status}'.")

        print("Scraping complete.")
        print(f"Total {total_count} records inserted/updated.")

        current_index += 1


if __name__ == "__main__":
    # inp = "https://www.goodreads.com/user/show/158454491, F, 23, https://www.goodreads.com/review/list/158454491"
    # scrape_and_store(inp)

    if len(sys.argv) < 3:
        print("Usage: python scrape_script.py <input_file> <start_index>")
        sys.exit(1)

    file_path = sys.argv[1]
    start_idx = int(sys.argv[2])

    scrape_and_store(file_path, start_idx)
