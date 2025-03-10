# from datetime import datetime
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from backend.schemas import CommentSchema  # , BookSchema, UserSchema, PostSchema
from backend.database import collections

books_collection = collections["Books"]
users_collection = collections["Users"]
posts_collection = collections["Posts"]
comments_collection = collections["Comments"]

# user_id and book_id need to be verified
# post_id needs to be verified
# parent_comment_id only needs to be verified if not None


def is_valid_object_id(
    collection_name, obj_id
):  # TODO: put in one file and just import it
    """
    Check if the given ObjectId exists in the specified collection.
    :param collection_name: The MongoDB collection name.
    :param obj_id: The ObjectId to be checked.
    :return: True if the ObjectId exists, False otherwise.
    """
    collection = collections[collection_name]
    return collection.find_one({"_id": ObjectId(obj_id)}) is not None


def create_comment(post_id, user_id, comment_text, parent_comment_id=0):
    try:
        # Validate post_id, user_id, and parent_comment_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        # Ensure parent_comment_id exists (if it's not 0, meaning it's a reply to an existing comment)
        if parent_comment_id != 0 and not is_valid_object_id(
            "Comments", parent_comment_id
        ):
            return "Error: Invalid parent_comment_id."

        # Prepare comment data
        comment_data = CommentSchema(
            post_id=post_id,
            user_id=user_id,
            comment_text=comment_text,
            parent_comment_id=parent_comment_id,
        )

        # Insert into MongoDB
        result = comments_collection.insert_one(comment_data.dict(by_alias=True))
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except DuplicateKeyError:
        return "Error: Duplicate comment!"
    except Exception as e:
        return f"Error: {str(e)}"


# Read a comment by its ID
def read_comment(comment_id):
    try:
        # Validate comment_id
        if not is_valid_object_id("Comments", comment_id):
            return "Error: Invalid comment_id."

        comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
        return (
            CommentSchema(**comment).model_dump(by_alias=True)
            if comment
            else "Comment not found."
        )

    except ValueError:
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


# Read a comment's field by field name
def read_comment_field(comment_id, field):
    try:
        # Validate comment_id
        if not is_valid_object_id("Comments", comment_id):
            return "Error: Invalid comment_id."

        comment = comments_collection.find_one(
            {"_id": ObjectId(comment_id)}, {field: 1, "_id": 0}
        )
        return comment[field] if comment else "Comment not found."

    except ValueError:
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def update_comment(comment_id, comment_text):
    try:
        # Validate comment_id
        if not is_valid_object_id("Comments", comment_id):
            return "Error: Invalid comment_id."

        # Prepare update data
        update_data = {"comment_text": comment_text}

        # Update the comment
        result = comments_collection.update_one(
            {"_id": ObjectId(comment_id)}, {"$set": update_data}
        )

        if result.matched_count:
            return "Comment updated successfully."
        else:
            return "Comment not found."

    except Exception as e:
        return f"Error: {str(e)}"


def delete_comment(comment_id):
    try:
        # Validate comment_id
        if not is_valid_object_id("Comments", comment_id):
            return "Error: Invalid comment_id."

        result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
        if result.deleted_count:
            return "Comment deleted successfully."
        else:
            return "Comment not found."
    except ValueError:
        return "Error: Invalid ObjectId format."
