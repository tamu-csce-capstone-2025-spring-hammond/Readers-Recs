# database/models/user_bookshelf.py
from datetime import datetime

from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from database import collections
from schemas import UserBookshelfSchema  # , BookSchema, UserSchema
from bson import ObjectId

books_collection = collections["Books"]
users_collection = collections["Users"]
user_bookshelf_collection = collections["User_Bookshelf"]

# user_bookshelf_collection.create_index([("user_id", 1), ("book_id", 1)], unique=True)


def is_valid_object_id(collection_name, obj_id):
    """
    Check if the given ObjectId exists in the specified collection.
    :param collection_name: The MongoDB collection name.
    :param obj_id: The ObjectId to be checked.
    :return: True if the ObjectId exists, False otherwise.
    """
    collection = collections[collection_name]
    return collection.find_one({"_id": ObjectId(obj_id)}) is not None


# user_id and book_id need to be verified
def create_user_bookshelf(
    user_id,
    book_id,
    status="to read",
    page_number=0,
    date_started=None,
    date_finished=None,
    rating="mid",
):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        existing = user_bookshelf_collection.find_one(
            {"user_id": user_id, "book_id": ObjectId(book_id)}
        )
        if existing:
            return "Error: book already present in user bookshelves."

        # Convert date_added to datetime if it's a datetime.date object
        date_added = datetime.today().date()  # Default to today's date
        if isinstance(date_added, datetime):
            date_added = datetime.combine(
                date_added.date(), datetime.min.time()
            )  # Ensure it's datetime, not date

        # Convert date_started and date_finished if they are datetime.date objects
        if date_started and isinstance(date_started, datetime):
            date_started = datetime.combine(date_started.date(), datetime.min.time())

        if date_finished and isinstance(date_finished, datetime):
            date_finished = datetime.combine(date_finished.date(), datetime.min.time())

        # Prepare data using UserBookshelfSchema
        user_bookshelf_data = UserBookshelfSchema(
            user_id=user_id,
            book_id=book_id,
            status=status,
            page_number=page_number,
            date_added=date_added,  # Correctly formatted date_added as datetime
            date_started=date_started,
            date_finished=date_finished,
            rating=rating,
        )

        data = user_bookshelf_data.model_dump(by_alias=True)
        if not data.get("_id"):
            data.pop("_id", None)

        # Insert into MongoDB
        result = user_bookshelf_collection.insert_one(data)
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except DuplicateKeyError:
        return "Error: User and Book combination must be unique!"
    except Exception as e:
        return f"Error: {str(e)}"


def update_user_bookshelf_status(user_id, book_id, new_status):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        # Validate new_status
        if new_status not in ["to read", "currently reading", "read"]:
            return "Error: Invalid status value."

        # Update the status
        result = user_bookshelf_collection.update_one(
            {"user_id": user_id, "book_id": book_id}, {"$set": {"status": new_status}}
        )

        if result.matched_count:
            return "UserBookshelf status updated successfully."
        else:
            return "UserBookshelf entry not found."

    except Exception as e:
        return f"Error: {str(e)}"


## GET BOOKSHELF TO PROCESS EXISTING HISTORY
def retrieve_user_bookshelf(user_id):
    # if not is_valid_object_id("Users", user_id):
    #         return "Error: Invalid user_id."

    books = list(user_bookshelf_collection.find({"user_id": user_id, "status": "read"}))
    return books  # returns list of books


def get_bookshelf_status(user_id, book_id):
    try:

        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        book = user_bookshelf_collection.find_one(
            {"user_id": user_id, "book_id": ObjectId(book_id)}
        )

        if book:
            return book.get("status", "status-error")
        else:
            return "no-status"

    except Exception as e:
        return f"Error: {str(e)}"


def get_read_books(user_id):
    try:
        # Validate user_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        # Get all books read by the user
        books = list(
            user_bookshelf_collection.find({"user_id": user_id, "status": "read"})
        )
        return books

    except Exception as e:
        return f"Error: {str(e)}"


def get_unread_books(user_id):
    try:
        # Validate user_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        # Get all books read by the user
        books = list(
            user_bookshelf_collection.find({"user_id": user_id, "status": "to-read"})
        )
        return books

    except Exception as e:
        return f"Error: {str(e)}"


def get_currently_reading_books(user_id):
    try:
        # Validate user_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        # Get all books read by the user
        books = list(
            user_bookshelf_collection.find(
                {"user_id": user_id, "status": "currently-reading"}
            )
        )
        if books:
            return books

    except Exception as e:
        return f"Error: {str(e)}"


def rate_book(user_id, book_id, new_rating):
    # TODO: add check that book has been completed
    shelf_entry = user_bookshelf_collection.find(
        {"user_id": user_id, "book_id": ObjectId(book_id), "status": "read"}
    )
    if not shelf_entry:
        return "Error: Book has not been read yet."
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        # Validate new_rating
        if new_rating not in ["pos", "neg", "mid"]:
            return "Error: Invalid rating value."

        # Update the rating
        result = user_bookshelf_collection.update_one(
            {"user_id": user_id, "book_id": ObjectId(book_id)},
            {"$set": {"rating": new_rating}},
        )

        if result.matched_count:
            return "UserBookshelf rating updated successfully."
        else:
            return "UserBookshelf entry not found."

    except Exception as e:
        return f"Error: {str(e)}"


### NEW METHODS FOR PAGE NUMBER
def update_page_number(user_id, book_id, new_page_number):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            print("Error: Invalid user id")
            return "Error: Invalid user_id."

        if not is_valid_object_id("Books", book_id):
            print("Error: Invalid book_id")
            return "Error: Invalid book_id."

        # Validate new_page_number
        if not isinstance(new_page_number, int) or new_page_number < 0:
            return "Error: Invalid page number. It must be a non-negative integer."

        # u_id = user_id
        # existing_entry = users_collection.find_one({"_id": u_id})
        # if not existing_entry:
        #     u_id = ObjectId(user_id)
        #     existing_entry = users_collection.find_one({"_id": u_id})
        #     if not existing_entry:
        #         print("Still no match for user_id.")
        #         print("Still no match for user_id.")

        # # existing_entry = books_collection.find_one({"_id": ObjectId(book_id)})
        # # if not existing_entry:
        # #     print("No matching entry found for book_id.")

        # existing_entry = user_bookshelf_collection.find_one({"user_id": user_id, "book_id": ObjectId(book_id)})
        # if not existing_entry:
        #     print("No matching entry found for user_id and book_id.")

        # Update the page number
        result = user_bookshelf_collection.update_one(
            {
                "user_id": user_id,
                "book_id": ObjectId(book_id),
                "status": "currently-reading",
            },
            {"$set": {"page_number": new_page_number}},
        )
        # print(result)
        # existing_entry = user_bookshelf_collection.find_one({"user_id": user_id, "book_id": ObjectId(book_id), "status": "currently-reading"})
        # if existing_entry:
        #     print("updated entry:", existing_entry)

        if result.matched_count:
            return "Page number updated successfully."
        else:
            print("UserBookshelf entry not found.")
            return "UserBookshelf entry not found."

    except Exception as e:
        return f"Error: {str(e)}"


def get_page_number(user_id, book_id):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."
        print("user id:", user_id)
        print("book_id:", book_id)
        # Retrieve the page number
        book_entry = user_bookshelf_collection.find_one(
            {
                "user_id": user_id,
                "book_id": ObjectId(book_id),
                "status": "currently-reading",
            }
        )

        if book_entry is not None:
            return book_entry.get("page_number", 0)
        else:
            return "UserBookshelf entry not found."

    except Exception as e:
        return f"Error: {str(e)}"


def delete_user_bookshelf(user_id, book_id):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        # Delete the document
        result = user_bookshelf_collection.delete_one(
            {"user_id": user_id, "book_id": ObjectId(book_id)}
        )
        if result.deleted_count:
            return "UserBookshelf entry deleted successfully."
        else:
            return "UserBookshelf entry not found."

    except Exception as e:
        return f"Error: {str(e)}"
