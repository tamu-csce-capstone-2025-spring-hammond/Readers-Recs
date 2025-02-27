from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from backend.schemas import BookSchema
from backend.database import collections
from pymongo.errors import PyMongoError

books_collection = collections["Books"]

# isbn and isbn13 need to be unique
books_collection.create_index("isbn", unique=True)
books_collection.create_index("isbn13", unique=True)

def create_book(title, author, page_count, genre, tags, publication_date, isbn, isbn13, cover_image, language, publisher, summary):
    try:
        # Ensure 'author' and 'tags' are lists
        if isinstance(author, str):
            author = [author]
        if isinstance(tags, str):
            tags = [tags]

        # Convert 'publication_date' to datetime
        publication_date = datetime.strptime(publication_date, "%Y-%m-%d")

        # Validate data using BookSchema
        book_data = BookSchema(
            title=title,
            author=author,
            page_count=page_count,
            genre=genre,
            tags=tags,
            publication_date=publication_date,
            isbn=isbn,
            isbn13=isbn13,
            cover_image=cover_image,
            language=language,
            publisher=publisher,
            summary=summary,
        )

        # Insert into MongoDB
        result = books_collection.insert_one(book_data.model_dump(by_alias=True))
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except DuplicateKeyError:
        return "Error: ISBN or ISBN-13 must be unique!"
    except ValueError:
        return "Error: Invalid date format. Use YYYY-MM-DD."
    
def read_book_field(book_id, field):
    book = books_collection.find_one({"_id": ObjectId(book_id)}, {field: 1, "_id": 0})
    if book:
        return book.get(field, "Field not found")
    else:
        return "Book not found"

def read_book_by_identifier(identifier, value):
    # value can be isbn, isbn13, or title
    if identifier not in ["title", "isbn", "isbn13"]:
        return "Error: Invalid identifier. Use 'title', 'isbn', or 'isbn13'."

    book = books_collection.find_one({identifier: value})

    if not book:
        return "Book not found."

    try:
        return BookSchema(**book).model_dump(by_alias=True)  # ✅ Use model_dump()
    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"

def read_book_title(book_id):
    return read_book_field(book_id, "title")

def read_book_author(book_id):
    return read_book_field(book_id, "author")

def read_book_page_count(book_id):
    return read_book_field(book_id, "page_count")

def read_book_genre(book_id):
    return read_book_field(book_id, "genre")

def read_book_tags(book_id):
    return read_book_field(book_id, "tags")

def read_book_publication_date(book_id):
    return read_book_field(book_id, "publication_date")

def read_book_isbn(book_id):
    return read_book_field(book_id, "isbn")

def read_book_isbn13(book_id):
    return read_book_field(book_id, "isbn13")

def read_book_cover_image(book_id):
    return read_book_field(book_id, "cover_image")

def read_book_language(book_id):
    return read_book_field(book_id, "language")

def read_book_publisher(book_id):
    return read_book_field(book_id, "publisher")

def read_book_summary(book_id):
    return read_book_field(book_id, "summary")

def read_book_genre_tags(book_id):
    return read_book_field(book_id, "genre_tags")

def update_book_details(book_id: str, **kwargs):
    try:
        book_id = ObjectId(book_id)

        # Fetch the existing book
        existing_book = books_collection.find_one({"_id": book_id})
        if not existing_book:
            return "Error: Book not found."

        # Merge existing data with new data
        updated_data = {**existing_book, **kwargs}

        # Validate and serialize the updated data
        validated_data = BookSchema(**updated_data).model_dump(by_alias=True)

        # Update the book in MongoDB
        books_collection.update_one({"_id": book_id}, {"$set": validated_data})
        return "Book updated successfully."

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except ValueError:
        return "Error: Invalid ObjectId format."

# functions for adding and removing specific list elements
def add_book_author(book_id, new_author):
    if not ObjectId.is_valid(book_id):
        return "Invalid book ID."

    if not new_author:
        return "Author name cannot be empty."

    try:
        result = books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$addToSet": {"author": new_author}}
        )
        if result.modified_count > 0:
            return "Author added successfully."
        else:
            return "Author was already in the list or book not found."
    except PyMongoError as e:
        return f"An error occurred: {str(e)}"

def add_book_tag(book_id, new_tag):
    if not ObjectId.is_valid(book_id):
        return "Invalid book ID."

    if not new_tag:
        return "Tag cannot be empty."

    try:
        result = books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$addToSet": {"tags": new_tag}}
        )
        if result.modified_count > 0:
            return "Tag added successfully."
        else:
            return "Tag was already in the list or book not found."
    except PyMongoError as e:
        return f"An error occurred: {str(e)}"

def remove_book_author(book_id, author_to_remove):
    if not ObjectId.is_valid(book_id):
        return "Invalid book ID."

    if not author_to_remove:
        return "Author name cannot be empty."

    try:
        result = books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$pull": {"author": author_to_remove}}
        )
        if result.modified_count > 0:
            return "Author removed successfully."
        else:
            return "Author not found in the list or book not found."
    except PyMongoError as e:
        return f"An error occurred: {str(e)}"

def remove_book_tag(book_id, tag_to_remove):
    if not ObjectId.is_valid(book_id):
        return "Invalid book ID."

    if not tag_to_remove:
        return "Tag cannot be empty."

    try:
        result = books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$pull": {"tags": tag_to_remove}}
        )
        if result.modified_count > 0:
            return "Tag removed successfully."
        else:
            return "Tag not found in the list or book not found."
    except PyMongoError as e:
        return f"An error occurred: {str(e)}"
 
def delete_book(book_id):
    try:
        book_id = ObjectId(book_id)

        # make sure the book exists before deleting
        if not books_collection.find_one({"_id": book_id}):
            return "Error: Book not found."

        db = collections

        # delete related records
        db["Posts"].delete_many({"book_id": book_id})
        db["Comments"].delete_many({"post_id": {"$in": [post["_id"] for post in db["Posts"].find({"book_id": book_id})]}})
        db["Chat_Messages"].delete_many({"chat_id": book_id})
        db["User_Bookshelf"].delete_many({"book_id": book_id})

        # delete the book
        books_collection.delete_one({"_id": book_id})
        return "Book and related records deleted successfully."

    except ValueError:
        return "Error: Invalid ObjectId format."