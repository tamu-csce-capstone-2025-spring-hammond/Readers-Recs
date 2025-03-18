# database/models/user_bookshelf.py
# from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from backend.database import collections
from backend.schemas import UserBookshelfSchema
from backend.mongo_id_utils import is_valid_object_id

books_collection = collections["Books"]
users_collection = collections["Users"]
user_bookshelf_collection = collections["UserBookshelf"]

user_bookshelf_collection.create_index([("user_id", 1), ("book_id", 1)], unique=True)


# user_id and book_id need to be verified
def create_user_bookshelf(
    user_id,
    book_id,
    status="To Read",
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

        # Prepare data using UserBookshelfSchema
        user_bookshelf_data = UserBookshelfSchema(
            user_id=user_id,
            book_id=book_id,
            status=status,
            page_number=page_number,
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
        if new_status not in ["To Read", "Currently Reading", "Read"]:
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


def rate_book(user_id, book_id, new_rating):
    # TODO: add check that book has been completed
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
            {"user_id": user_id, "book_id": book_id}, {"$set": {"rating": new_rating}}
        )

        if result.matched_count:
            return "UserBookshelf rating updated successfully."
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
            {"user_id": user_id, "book_id": book_id}
        )
        if result.deleted_count:
            return "UserBookshelf entry deleted successfully."
        else:
            return "UserBookshelf entry not found."

    except Exception as e:
        return f"Error: {str(e)}"
