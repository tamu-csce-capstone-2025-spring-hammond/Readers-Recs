from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from backend.schemas import BookSchema, UserSchema, PostSchema, CommentSchema
from backend.database import collections

books_collection = collections["Books"]
users_collection = collections["Users"]
posts_collection = collections["Posts"]
comments_collection = collections["Comments"]

# user_id and book_id need to be verified
# post_id needs to be verified
# parent_comment_id only needs to be verified if not None