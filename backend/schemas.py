from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date

# Custom ObjectId validator for MongoDB
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)

# -----------------------------------------------
# BOOKS SCHEMA
# -----------------------------------------------
class BookSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")  # ✅ Fixed `_id` issue
    author: str
    title: str
    page_count: int
    genre: str
    publication_date: datetime
    isbn: str
    isbn13: str
    cover_image: str
    language: str
    publisher: str
    tags: List[str]

    class Config:
        populate_by_name = True

# -----------------------------------------------
# USERS SCHEMA
# -----------------------------------------------
class OAuthSchema(BaseModel):
    refresh_token: str
    access_token: str

class UserSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")  # ✅ Fixed `_id`
    first_name: str
    last_name: str
    username: str
    email_address: EmailStr
    oauth: OAuthSchema
    interests: List[str]
    profile_image: str
    demographics: List[str]

    class Config:
        populate_by_name = True

# -----------------------------------------------
# USER_BOOKSHELF SCHEMA (Junction Table)
# -----------------------------------------------
class UserBookshelfSchema(BaseModel):
    user_id: PyObjectId
    book_id: PyObjectId
    status: str = Field(..., pattern=r"(?i)^(To Read|Currently Reading|Read)$")
    page_number: int
    date_added: date
    date_started: Optional[date] = None
    date_finished: Optional[date] = None
    rating: Optional[str] = Field(None, pattern=r"(?i)^(pos|neg|mid)$")

# -----------------------------------------------
# POSTS SCHEMA
# -----------------------------------------------
class PostSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")  # ✅ Fixed `_id`
    user_id: PyObjectId
    book_id: PyObjectId
    title: str
    post_text: str
    date_posted: datetime
    date_edited: datetime
    Tags: List[str]

    class Config:
        populate_by_name = True

# -----------------------------------------------
# COMMENTS SCHEMA
# -----------------------------------------------
class CommentSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")  # ✅ Fixed `_id`
    post_id: PyObjectId
    user_id: PyObjectId
    parent_comment_id: Optional[int] = None
    comment_text: str
    date_posted: datetime
    date_edited: datetime

    class Config:
        populate_by_name = True

# -----------------------------------------------
# CHAT_MESSAGES SCHEMA
# -----------------------------------------------
class ChatMessageSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")  # ✅ Fixed `_id`
    book_id: PyObjectId
    user_id: PyObjectId
    message_text: str
    date_posted: datetime
    date_edited: datetime

    class Config:
        populate_by_name = True