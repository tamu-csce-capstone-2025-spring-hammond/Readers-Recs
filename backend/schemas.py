# backend/schemas.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List
from bson import ObjectId
from datetime import datetime, date

# from collections import defaultdict
# import numpy as np


# Custom ObjectId validator for MongoDB
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler=None):
        from pydantic_core.core_schema import no_info_plain_validator_function

        def validate(v, info):
            if not ObjectId.is_valid(v):
                raise ValueError(f"Invalid ObjectId: {v}")
            return str(v)

        return no_info_plain_validator_function(validate)


# -----------------------------------------------
# BOOKS SCHEMA
# -----------------------------------------------
class BookSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author: List[str] = Field(default_factory=list)
    title: str = Field(default="Unknown Title")
    page_count: int = Field(default=0)
    genre: str = Field(default="Unknown Genre")
    publication_date: datetime = Field(default_factory=datetime.now)
    isbn: str = Field(default="000-0000000000")
    isbn13: str = Field(default="0000000000000")
    cover_image: str = Field(default="default_cover_image.jpg")
    language: str = Field(default="eng")
    publisher: str = Field(default="Unknown Publisher")
    tags: List[str] = Field(default_factory=list)
    summary: str = Field(default="No summary available.")
    genre_tags: List[str] = Field(default_factory=list)
    embedding: List[float] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# USERS SCHEMA
# -----------------------------------------------
class OAuthSchema(BaseModel):
    refresh_token: str = Field(default="default_refresh_token")
    access_token: str = Field(default="default_access_token")


class DemographicSchema(BaseModel):  # TODO: update based on demographics decisions
    gender: str = Field(default="Not Specified")
    age: int = Field(default=0)
    country: str = Field(default="Not Specified")
    birthday: date = Field(default_factory=date.today)


class UserSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str = Field(default="First Name")
    last_name: str = Field(default="Last Name")
    username: str = Field(default="username")
    email_address: EmailStr = Field(default="user@example.com")
    oauth: OAuthSchema = Field(default_factory=OAuthSchema)
    interests: List[str] = Field(default_factory=list)
    profile_image: str = Field(default="default_profile_image.jpg")
    demographics: DemographicSchema = Field(default_factory=DemographicSchema)
    genre_weights: dict[str, float] = Field(
        default_factory=dict
    )  # TODO: discuss. store as an object?
    embedding: List[float] = Field(default_factory=list)
    genre_tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# USER_BOOKSHELF SCHEMA (Junction Table)
# -----------------------------------------------
class UserBookshelfSchema(BaseModel):
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    book_id: PyObjectId = Field(default_factory=PyObjectId)
    status: str = Field(
        default="To Read", pattern=r"(?i)^(To Read|Currently Reading|Read)$"
    )
    page_number: int = Field(default=0)
    date_added: date = Field(default_factory=date.today)
    date_started: date = Field(default_factory=date.today)
    date_finished: date = Field(default_factory=date.today)
    rating: str = Field(default="mid", pattern=r"(?i)^(pos|neg|mid)$")


# -----------------------------------------------
# POSTS SCHEMA
# -----------------------------------------------
class PostSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    book_id: PyObjectId = Field(default_factory=PyObjectId)
    title: str = Field(default="Untitled Post")
    post_text: str = Field(default="No content provided.")
    date_posted: datetime = Field(default_factory=datetime.now)
    date_edited: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# COMMENTS SCHEMA
# -----------------------------------------------
class CommentSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_id: PyObjectId = Field(default_factory=PyObjectId)
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    parent_comment_id: int = Field(default=0)
    comment_text: str = Field(default="No content provided.")
    date_posted: datetime = Field(default_factory=datetime.now)
    date_edited: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# CHAT_MESSAGES SCHEMA
# -----------------------------------------------
class ChatMessageSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    book_id: PyObjectId = Field(default_factory=PyObjectId)
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    message_text: str = Field(default="No content provided.")
    date_posted: datetime = Field(default_factory=datetime.now)
    date_edited: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(populate_by_name=True)
