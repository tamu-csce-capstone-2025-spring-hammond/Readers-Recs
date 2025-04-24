# database/models/comments.py
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pydantic import ValidationError
from schemas import CommentSchema
from mongo_id_utils import is_valid_object_id
from database import collections
import pytz

books_collection = collections["Books"]
users_collection = collections["Users"]
posts_collection = collections["Posts"]
comments_collection = collections["Comments"]

# user_id and book_id need to be verified
# post_id needs to be verified
# parent_comment_id only needs to be verified if not None


def create_comment(post_id, user_id, comment_text, parent_comment_id=None):
    try:
        if (
            not comment_text
            or not isinstance(comment_text, str)
            or not comment_text.strip()
        ):
            return "Error: comment_text cannot be empty."

        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        if parent_comment_id and not is_valid_object_id("Comments", parent_comment_id):
            return "Error: Invalid parent_comment_id."

        comment_data = CommentSchema(
            post_id=post_id,
            user_id=user_id,
            comment_text=comment_text.strip(),
            parent_comment_id=parent_comment_id,
        )

        data = comment_data.model_dump(by_alias=True)
        data.pop("_id", None)

        result = comments_collection.insert_one(data)
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def create_initial_comment(post_id, user_id, comment_text):
    """
    Creates a top-level comment (i.e. not a reply).
    """
    return create_comment(post_id, user_id, comment_text, parent_comment_id=None)


def reply_to_comment(post_id, user_id, comment_text, parent_comment_id):
    """
    Creates a reply to an existing comment.
    """
    if not parent_comment_id:
        return "Error: parent_comment_id cannot be None for replies."
    return create_comment(post_id, user_id, comment_text, parent_comment_id)


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

    except (ValueError, InvalidId):
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

        if field in comment:
            return comment[field]
        else:
            return f"Field '{field}' not found in comment."

    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def update_comment(comment_id, comment_text):
    try:
        # Validate comment_id
        if not is_valid_object_id("Comments", comment_id):
            return "Error: Invalid comment_id."

        if not comment_text or comment_text.strip() == "":
            return "Error: comment_text cannot be empty."

        # Prepare update data including the date_edited field
        update_data = {
            "comment_text": comment_text,
            "date_edited": datetime.now(pytz.timezone("America/Chicago")),
        }

        # Update the comment
        result = comments_collection.update_one(
            {"_id": ObjectId(comment_id)}, {"$set": update_data}
        )

        if result.matched_count:
            return "Comment updated successfully."
        else:
            return "Comment not found."
    except InvalidId:
        return "Error: Invalid ObjectId format."
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
    except (ValueError, InvalidId):
        return "Error: Invalid comment_id."
    except Exception as e:
        return f"Error: {str(e)}"


# Used to delete all comments associated with a post when the post is deleted
def delete_comments_by_post(post_id):
    try:
        # Validate post_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        result = comments_collection.delete_many({"post_id": ObjectId(post_id)})
        if result.deleted_count:
            return f"{result.deleted_count} comments deleted."
        else:
            return "No comments found for this post."

    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def get_all_comments_for_post(post_id):
    try:
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        comments = list(comments_collection.find({"post_id": ObjectId(post_id)}))

        # Convert ObjectIds to strings
        comment_dict = {
            str(comment["_id"]): serialize_comment(comment) for comment in comments
        }

        nested_comments = []
        for comment in comment_dict.values():
            user = users_collection.find_one({"_id": ObjectId(comment["user_id"])})
            if user:
                comment["username"] = user.get("username", "Unknown User")
                comment["profile_picture"] = user.get("profile_image", "")

            parent_id = comment.get("parent_comment_id")
            if parent_id and parent_id in comment_dict:
                parent = comment_dict[parent_id]
                if "replies" not in parent:
                    parent["replies"] = []
                parent["replies"].append(comment)
            else:
                nested_comments.append(comment)

        return nested_comments

    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


# used to convert ObjectId to string and copy comment_text to content
def serialize_comment(comment):
    serialized = {}
    for key, value in comment.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    # copy comment_text to content
    if "comment_text" in serialized:
        serialized["content"] = serialized["comment_text"]
    return serialized
