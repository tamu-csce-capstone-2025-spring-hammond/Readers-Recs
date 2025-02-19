from pymongo import errors
from bson import ObjectId
import logging
from schemas import (
    BookSchema, UserSchema, UserBookshelfSchema, PostSchema,
    CommentSchema, ChatMessageSchema
)
from database import collections

logging.basicConfig(level=logging.ERROR)

schema_map = {
    "Books": BookSchema,
    "Users": UserSchema,
    "User_Bookshelf": UserBookshelfSchema,
    "Posts": PostSchema,
    "Comments": CommentSchema,
    "Chat_Messages": ChatMessageSchema,
}

# -----------------------------------------------
# CREATE
# -----------------------------------------------
def insert_document(collection_name: str, data: dict):
    if collection_name not in collections:
        return "Error: Invalid collection name"

    try:
        schema = schema_map[collection_name]
        validated_data = schema(**data).model_dump(by_alias=True)

        result = collections[collection_name].insert_one(validated_data)
        return collections[collection_name].find_one({"_id": result.inserted_id})

    except ValueError as e:
        logging.error(f"Validation Error: {e}")
        return f"Validation Error: {e}"

    except errors.DuplicateKeyError:
        logging.error("Duplicate Key Error: This record already exists.")
        return "Duplicate Key Error: This record already exists."

    except Exception as e:
        logging.error(f"Database Error: {e}")
        return f"Database Error: {e}"

# -----------------------------------------------
# READ
# -----------------------------------------------
def get_document_by_id(collection_name: str, doc_id: str):
    if collection_name not in collections:
        return "Error: Invalid collection name"

    if not ObjectId.is_valid(doc_id):
        return "Error: Invalid ObjectId format"

    doc = collections[collection_name].find_one({"_id": ObjectId(doc_id)})
    return doc if doc else "Error: Document not found"

# -----------------------------------------------
# UPDATE
# -----------------------------------------------
def update_document(collection_name: str, doc_id: str, updates: dict):
    if collection_name not in collections:
        return "Error: Invalid collection name"

    if not ObjectId.is_valid(doc_id):
        return "Error: Invalid ObjectId format"

    try:
        result = collections[collection_name].update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": updates}
        )

        if result.modified_count == 0:
            return "Error: Document not updated (either not found or no changes applied)"

        return collections[collection_name].find_one({"_id": ObjectId(doc_id)})

    except Exception as e:
        logging.error(f"Database Error: {e}")
        return f"Database Error: {e}"

# -----------------------------------------------
# DELETE
# -----------------------------------------------
def delete_document(collection_name: str, doc_id: str):
    if collection_name not in collections:
        return "Error: Invalid collection name"

    if not ObjectId.is_valid(doc_id):
        return "Error: Invalid ObjectId format"

    result = collections[collection_name].delete_one({"_id": ObjectId(doc_id)})
    return True if result.deleted_count == 1 else "Error: Document not found"
