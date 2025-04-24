# backend/schemas.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Dict, List, Optional
from bson import ObjectId
from datetime import datetime, date
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
import pytz


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source, handler: GetCoreSchemaHandler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema):
        return {"type": "string"}


# -----------------------------------------------
# BOOKS SCHEMA
# -----------------------------------------------
class BookSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author: List[str] = Field(default_factory=list)
    title: str = Field(default="Unknown Title")
    page_count: int = Field(default=0)
    genre: str = Field(default="Unknown Genre")
    publication_date: Optional[date] = None
    isbn: str = Field(default="000000000")
    isbn13: str = Field(default="0000000000000")
    cover_image: str = Field(default="default_cover_image.jpg")
    language: str = Field(default="eng")
    publisher: str = Field(default="Unknown Publisher")
    tags: List[str] = Field(default_factory=list)
    summary: str = Field(default="No summary available.")
    genre_tags: List[str] = Field(default_factory=list)
    embedding: List[float] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("publication_date", mode="before")
    def ensure_date(cls, v):
        if isinstance(v, datetime):
            # Strip time
            v = v.date()

        # Handle string input (e.g., from JSON)
        if isinstance(v, str):
            try:
                v = datetime.fromisoformat(v).date()
            except ValueError:
                raise ValueError("Invalid date string format for publication_date")

        # If the date is in the future (likely due to default), return None
        if isinstance(v, date) and v > date.today():
            return None

        return v


# -----------------------------------------------
# USERS SCHEMA
# -----------------------------------------------
class OAuthSchema(BaseModel):
    refresh_token: str = Field(default="default_refresh_token")
    access_token: str = Field(default="default_access_token")


class DemographicSchema(BaseModel):
    gender: str = Field(default="")
    age: int = Field(default=0)
    country: str = Field(default="")
    birthday: Optional[date] = Field(default=None)


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
    genre_weights: Dict[str, float] = Field(default_factory=dict)
    embedding: List[float] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# USER_BOOKSHELF SCHEMA (Junction Table)
# -----------------------------------------------
class UserBookshelfSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(default="userid")
    book_id: PyObjectId = Field(default_factory=PyObjectId)
    status: str = Field(
        default="to-read", pattern=r"(?i)^(to-read|currently-reading|read)$"
    )
    page_number: int = Field(default=0)
    date_added: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )
    date_started: Optional[datetime] = None
    date_finished: Optional[datetime] = None
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
    date_posted: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )
    date_edited: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# COMMENTS SCHEMA
# -----------------------------------------------
class CommentSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_id: PyObjectId = Field(default_factory=PyObjectId)
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    parent_comment_id: Optional[PyObjectId] = None
    comment_text: str = Field(default="No content provided.")
    date_posted: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )
    date_edited: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )

    model_config = ConfigDict(populate_by_name=True)


# -----------------------------------------------
# CHAT_MESSAGES SCHEMA
# -----------------------------------------------
class ChatMessageSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    book_id: PyObjectId = Field(default_factory=PyObjectId)
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    message_text: str = Field(default="No content provided.")
    date_posted: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )
    date_edited: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Chicago"))
    )

    model_config = ConfigDict(populate_by_name=True)
