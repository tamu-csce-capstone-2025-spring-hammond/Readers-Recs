from bson.objectid import ObjectId

# from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from database import collections
from schemas import UserBookshelfSchema  # , BookSchema, UserSchema

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

        # Prepare data
        user_bookshelf_data = UserBookshelfSchema(
            user_id=user_id,
            book_id=book_id,
            status=status,
            page_number=page_number,
            date_started=date_started,
            date_finished=date_finished,
            rating=rating,
        )

        # Insert into MongoDB
        result = user_bookshelf_collection.insert_one(
            user_bookshelf_data.dict(by_alias=True)
        )
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
    
    books = list(
        user_bookshelf_collection.find(
            {"user_id": user_id, "status": "read"}
        )
    )
    return books     # returns list of books



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
