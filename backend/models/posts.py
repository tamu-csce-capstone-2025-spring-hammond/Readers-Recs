from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from backend.schemas import BookSchema, UserSchema, PostSchema
from backend.database import collections

books_collection = collections["Books"]
users_collection = collections["Users"]
posts_collection = collections["Posts"]

# user_id and book_id need to be verified