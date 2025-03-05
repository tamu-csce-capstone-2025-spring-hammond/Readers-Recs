from bson.objectid import ObjectId

# from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from backend.schemas import PostSchema  # , BookSchema, UserSchema
from backend.database import collections

books_collection = collections["Books"]
users_collection = collections["Users"]
posts_collection = collections["Posts"]

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
    collection = collections[collection_name]
    return collection.find_one({"_id": ObjectId(obj_id)}) is not None


def create_post(user_id, book_id, title, post_text, tags):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."

        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        # Prepare post data
        post_data = PostSchema(
            user_id=user_id,
            book_id=book_id,
            title=title,
            post_text=post_text,
            tags=tags if isinstance(tags, list) else [tags],
        )

        # Insert into MongoDB
        result = posts_collection.insert_one(post_data.dict(by_alias=True))
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except DuplicateKeyError:
        return "Error: Duplicate post!"
    except Exception as e:
        return f"Error: {str(e)}"


def read_post(post_id):
    try:
        # Validate post_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        return (
            PostSchema(**post).model_dump(by_alias=True) if post else "Post not found."
        )

    except ValueError:
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


# Read a post's field by field name
def read_post_field(post_id, field):
    try:
        # Validate post_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        post = posts_collection.find_one(
            {"_id": ObjectId(post_id)}, {field: 1, "_id": 0}
        )
        return post[field] if post else "Post not found."

    except ValueError:
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def update_post(post_id, title=None, post_text=None, tags=None):
    try:
        # Validate post_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        # Prepare update data
        update_data = {}
        if title:
            update_data["title"] = title
        if post_text:
            update_data["post_text"] = post_text
        if tags:
            update_data["tags"] = tags if isinstance(tags, list) else [tags]

        # Update the post
        result = posts_collection.update_one(
            {"_id": ObjectId(post_id)}, {"$set": update_data}
        )

        if result.matched_count:
            return "Post updated successfully."
        else:
            return "Post not found."

    except Exception as e:
        return f"Error: {str(e)}"


def delete_post(post_id):
    try:
        # Validate post_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        result = posts_collection.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count:
            return "Post deleted successfully."
        else:
            return "Post not found."
    except ValueError:
        return "Error: Invalid ObjectId format."
