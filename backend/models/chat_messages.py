# database/models/chat_messages.py
from bson.objectid import ObjectId

# from datetime import datetime
# from pymongo.errors import DuplicateKeyError
# from pydantic import ValidationError
# from backend.schemas import BookSchema, UserSchema, ChatMessageSchema
from backend.database import collections

# books_collection = collections["Books"]
# users_collection = collections["Users"]


# user_id and book_id need to be verified
def is_valid_object_id(
    collection_name, obj_id
):  # TODO: put in one file and just import it
    """
    Check if the given ObjectId exists in the specified collection.
    :param collection_name: The MongoDB collection name.
    :param obj_id: The ObjectId to be checked.
    :return: True if the ObjectId exists, False otherwise.
    """

    if collection_name not in collections:
        return False
    elif collection_name == "Users" or collection_name == "User_Bookshelf":
        collection = collections[collection_name]
        return collection.find_one({"_id": obj_id}) is not None
    else:
        collection = collections[collection_name]
        return collection.find_one({"_id": ObjectId(obj_id)}) is not None
