from bson.objectid import ObjectId
from datetime import datetime
from pydantic import ValidationError
from zoneinfo import ZoneInfo
from backend.schemas import PostSchema
from backend.database import collections
from backend.models.comments import delete_comments_by_post
from backend.mongo_id_utils import is_valid_object_id

posts_collection = collections["Posts"]


# user_id and book_id need to be verified
def create_post(user_id, book_id, title, post_text, tags):
    try:
        # Validate user_id and book_id
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        # Prepare post data using PostSchema
        post_data = PostSchema(
            user_id=user_id,
            book_id=book_id,
            title=title,
            post_text=post_text,
            tags=tags if isinstance(tags, list) else [tags],
        )

        data = post_data.model_dump(by_alias=True)
        if not data.get("_id"):
            data.pop("_id", None)
        result = posts_collection.insert_one(data)
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    # except DuplicateKeyError:
    #     return "Error: Duplicate post!"
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


def update_post(post_id, title="", post_text="", tags=None):
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
        if tags is not None:
            update_data["tags"] = tags if isinstance(tags, list) else [tags]

        # Update the date_edited field using a timezone-aware datetime for America/Chicago
        update_data["date_edited"] = datetime.now(ZoneInfo("America/Chicago"))

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

        # delete post and associated comments
        delete_comments_by_post(post_id)
        result = posts_collection.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count:
            return "Post deleted successfully."
        else:
            return "Post not found."
    except ValueError:
        return "Error: Invalid ObjectId format."


def get_all_posts_for_book(book_id):
    try:
        # Validate book_id
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."

        posts = posts_collection.find({"book_id": ObjectId(book_id)})
        return [PostSchema(**post).model_dump(by_alias=True) for post in posts]

    except Exception as e:
        return f"Error: {str(e)}"
