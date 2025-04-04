# database/models/comments.py
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from zoneinfo import ZoneInfo
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
        # Validate post_id, user_id, and parent_comment_id
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        # Ensure parent_comment_id exists (if it's not None, it's a reply to an existing comment)
        if parent_comment_id and not is_valid_object_id("Comments", parent_comment_id):
            return "Error: Invalid parent_comment_id."

        # Prepare comment data using CommentSchema
        comment_data = CommentSchema(
            post_id=post_id,
            user_id=user_id,
            comment_text=comment_text,
            parent_comment_id=parent_comment_id,
        )

        data = comment_data.model_dump(by_alias=True)
        if not data.get("_id"):
            data.pop("_id", None)

        result = comments_collection.insert_one(data)
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except DuplicateKeyError:
        return "Error: Duplicate comment!"
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

        if field in comment:
            return comment[field]
        else:
            return f"Field '{field}' not found in comment."

    except ValueError:
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def update_comment(comment_id, comment_text):
    try:
        # Validate comment_id
        if not is_valid_object_id("Comments", comment_id):
            return "Error: Invalid comment_id."

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

    except ValueError:
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def stringify_object_ids(comment):
    comment["_id"] = str(comment["_id"])
    if comment.get("user_id"):
        comment["user_id"] = str(comment["user_id"])
    if comment.get("post_id"):
        comment["post_id"] = str(comment["post_id"])
    if comment.get("parent_comment_id"):
        comment["parent_comment_id"] = str(comment["parent_comment_id"])
    # recursively fix replies if any
    if "replies" in comment:
        for reply in comment["replies"]:
            stringify_object_ids(reply)
    return comment


def get_all_comments_for_post(post_id):
    try:
        if not is_valid_object_id("Posts", post_id):
            return "Error: Invalid post_id."

        comments_cursor = comments_collection.find({"post_id": ObjectId(post_id)})
        comment_map = {}

        # Load and validate all comments
        for comment in comments_cursor:
            try:
                validated_comment = CommentSchema(**comment).model_dump(by_alias=True)
                validated_comment["replies"] = []
                comment_id = str(validated_comment["_id"])
                comment_map[comment_id] = validated_comment
            except Exception as e:
                print(f"Skipping invalid comment: {e}")
                continue

        # Organize into tree
        root_comments = []
        for comment_id, comment in comment_map.items():
            parent_id = comment.get("parent_comment_id")
            if parent_id:
                parent_id = str(parent_id)
                parent_comment = comment_map.get(parent_id)
                if parent_comment:
                    parent_comment["replies"].append(comment)
            else:
                root_comments.append(comment)

        return [stringify_object_ids(comment) for comment in root_comments]

    except Exception as e:
        return f"Error: {str(e)}"
