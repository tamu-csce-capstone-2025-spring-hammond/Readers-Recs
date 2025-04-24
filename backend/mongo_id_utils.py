# backend/objectid_utils.py
from bson.objectid import ObjectId
from database import collections
from bson.errors import InvalidId


def is_valid_object_id(collection_name, obj_id):
    """
    Check if the given ObjectId exists in the specified collection.
    :param collection_name: The MongoDB collection name.
    :param obj_id: The ObjectId to be checked.
    :return: True if the ObjectId exists, False otherwise.
    """

    try:
        if collection_name not in collections:
            return False
        elif collection_name == "Users" or collection_name == "User_Bookshelf":
            # check with both string and ObjectId
            collection = collections[collection_name]
            if (
                collection.find_one({"_id": ObjectId(obj_id)}) is not None
                or collection.find_one({"_id": obj_id}) is not None
            ):
                return True
            else:
                return collection.find_one({"_id": ObjectId(obj_id)}) is not None
        else:
            collection = collections[collection_name]
            return collection.find_one({"_id": ObjectId(obj_id)}) is not None
    except InvalidId:
        return False
