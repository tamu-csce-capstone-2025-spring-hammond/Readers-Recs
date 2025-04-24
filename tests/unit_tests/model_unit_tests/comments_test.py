import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from datetime import datetime
import pytz
from models.comments import (
    create_comment,
    create_initial_comment,
    reply_to_comment,
    read_comment,
    read_comment_field,
    update_comment,
    delete_comment,
    delete_comments_by_post,
    get_all_comments_for_post,
    serialize_comment,
)
import models.comments as comment_model
from bson.errors import InvalidId

VALID_POST_ID = "507f1f77bcf86cd799439011"
VALID_USER_ID = "507f1f77bcf86cd799439012"
VALID_COMMENT_TEXT = "This is a test comment"
VALID_PARENT_ID = "507f1f77bcf86cd799439013"


@pytest.fixture(autouse=True)
def mock_comments_collections(monkeypatch):
    fake_id = ObjectId()
    fake_post_id = ObjectId()
    fake_user_id = ObjectId()
    mock_comment = {
        "_id": fake_id,
        "post_id": fake_post_id,
        "user_id": fake_user_id,
        "comment_text": "test",
        "date_posted": datetime.now(pytz.timezone("America/Chicago")),
        "date_edited": datetime.now(pytz.timezone("America/Chicago")),
    }
    mock_comments = MagicMock()
    mock_comments.insert_one.return_value.inserted_id = fake_id
    mock_comments.find_one.side_effect = lambda q, *_: (
        mock_comment if q.get("_id") == fake_id else None
    )
    mock_comments.update_one.return_value.modified_count = 1
    mock_comments.delete_one.return_value.deleted_count = 1
    mock_comments.delete_many.return_value.deleted_count = 0
    mock_comments.find.return_value = [mock_comment]

    monkeypatch.setitem(comment_model.collections, "Comments", mock_comments)
    monkeypatch.setattr(comment_model, "comments_collection", mock_comments)

    mock_users = MagicMock()
    mock_users.find_one.return_value = {"username": "tester", "profile_image": ""}
    monkeypatch.setitem(comment_model.collections, "Users", mock_users)
    monkeypatch.setattr(comment_model, "users_collection", mock_users)

    mock_posts = MagicMock()
    mock_posts.find_one.return_value = True
    mock_posts.find.return_value = [{"_id": ObjectId()}]
    mock_posts.delete_many.return_value.deleted_count = 1
    monkeypatch.setitem(comment_model.collections, "Posts", mock_posts)
    monkeypatch.setattr(comment_model, "posts_collection", mock_posts)

    return str(fake_user_id), str(fake_post_id), str(fake_id)


def test_create_initial_comment():
    result = create_initial_comment(ObjectId(), ObjectId(), "content")
    assert isinstance(result, str)


def test_reply_to_comment():
    result = reply_to_comment(ObjectId(), ObjectId(), "reply", ObjectId())
    assert isinstance(result, str)


def test_read_comment(mock_comments_collections):
    _, _, comment_id = mock_comments_collections
    comment = read_comment(comment_id)
    assert isinstance(comment, dict)
    assert comment["comment_text"] == "test"


def test_read_comment_field(mock_comments_collections):
    _, _, comment_id = mock_comments_collections
    result = read_comment_field(comment_id, "comment_text")
    assert result == "test"


def test_update_comment(mock_comments_collections):
    _, _, comment_id = mock_comments_collections
    result = update_comment(comment_id, "Updated")
    assert result == "Comment updated successfully."


def test_delete_comment(mock_comments_collections):
    _, _, comment_id = mock_comments_collections
    result = delete_comment(comment_id)
    assert result == "Comment deleted successfully."


def test_delete_comments_by_post():
    result = delete_comments_by_post(ObjectId())
    assert result in ["No comments found for this post.", "1 comments deleted."]


def test_get_all_comments_for_post():
    comments = get_all_comments_for_post(ObjectId())
    assert isinstance(comments, list)
    assert len(comments) > 0
    assert "username" in comments[0]
    assert "profile_picture" in comments[0]


def test_serialize_comment_format():
    comment_data = {
        "_id": ObjectId(),
        "post_id": ObjectId(),
        "user_id": ObjectId(),
        "comment_text": "test content",
        "date_posted": datetime.now(pytz.timezone("America/Chicago")),
        "date_edited": datetime.now(pytz.timezone("America/Chicago")),
    }
    result = serialize_comment(comment_data)
    assert result["content"] == "test content"
    assert isinstance(result["_id"], str)
    assert isinstance(result["post_id"], str)
    assert isinstance(result["user_id"], str)


def test_get_all_comments_for_post_invalid():
    result = get_all_comments_for_post("bad")
    assert result in "Error: Invalid post_id."


def test_reply_to_comment_invalid_post_id():
    res = reply_to_comment("badid", str(ObjectId()), "text", str(ObjectId()))
    assert res.startswith("Error:")


def test_reply_to_comment_invalid_user_id():
    res = reply_to_comment(str(ObjectId()), "badid", "text", str(ObjectId()))
    assert res.startswith("Error:")


def test_reply_to_comment_invalid_parent_id():
    res = reply_to_comment(str(ObjectId()), str(ObjectId()), "text", "notanid")
    assert res == "Error: Invalid parent_comment_id."


def test_reply_to_comment_missing_text():
    res = reply_to_comment(str(ObjectId()), str(ObjectId()), "", str(ObjectId()))
    assert res == "Error: comment_text cannot be empty."


def test_read_comment_field_invalid_id():
    result = read_comment_field("badid", "comment_text")
    assert result.startswith("Error:")


def test_read_comment_field_not_found(monkeypatch, mock_comments_collections):
    _, _, comment_id = mock_comments_collections
    result = read_comment_field(comment_id, "invalid_field")
    assert result == "Field 'invalid_field' not found in comment."


def test_update_comment_invalid_id():
    result = update_comment("notanid", "new content")
    assert result.startswith("Error:")


def test_update_comment_missing_content(mock_comments_collections):
    _, _, comment_id = mock_comments_collections
    result = update_comment(comment_id, None)
    assert result.startswith("Error: comment_text cannot be empty.")


def test_delete_comments_by_post_invalid_id():
    result = delete_comments_by_post("notanid")
    assert result == "Error: Invalid post_id."


def test_read_comment_invalid_id():
    result = read_comment("notanid")
    assert result == "Error: Invalid comment_id."


def test_read_comment_not_found(monkeypatch):
    fake_id = str(ObjectId())
    monkeypatch.setattr(comment_model.comments_collection, "find_one", lambda q: None)
    result = read_comment(fake_id)
    assert result == "Error: Invalid comment_id."


def test_delete_comment_invalid_id():
    result = delete_comment("notanid")
    assert result == "Error: Invalid comment_id."


def test_delete_comment_not_found(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.delete_one.return_value.deleted_count = 0
    monkeypatch.setattr(comment_model, "comments_collection", mock_col)
    result = delete_comment(fake_id)
    assert result == "Error: Invalid comment_id."


@patch("models.comments.comments_collection.find_one", side_effect=Exception("Crash"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_read_comment_field_exception(mock_valid, mock_find):
    result = read_comment_field("68094b3267aa3dbf50919a52", "comment_text")
    assert result == "Error: Crash"


@patch("models.comments.comments_collection.delete_one", side_effect=Exception("Boom"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_delete_comment_exception(mock_valid, mock_delete):
    result = delete_comment("68094b3267aa3dbf50919a52")
    assert result == "Error: Boom"


@patch(
    "models.comments.comments_collection.delete_many", side_effect=Exception("Crash")
)
@patch("models.comments.is_valid_object_id", return_value=True)
def test_delete_comments_by_post_exception(mock_valid, mock_delete):
    result = delete_comments_by_post("68094b3267aa3dbf50919a52")
    assert result == "Error: Crash"


@patch(
    "models.comments.comments_collection.find",
    side_effect=Exception("Database failure"),
)
@patch("models.comments.is_valid_object_id", return_value=True)
def test_get_all_comments_exception(mock_valid, mock_find):
    result = get_all_comments_for_post("68094b3267aa3dbf50919a52")
    assert result == "Error: Database failure"


@patch("models.comments.comments_collection.insert_one")
@patch("models.comments.CommentSchema")
@patch("models.comments.is_valid_object_id", side_effect=InvalidId("bad id"))
def test_create_comment_invalidid(mock_valid, mock_schema, mock_insert):
    result = create_comment(VALID_POST_ID, VALID_USER_ID, VALID_COMMENT_TEXT)
    assert result == "Error: Invalid ObjectId format."


@patch(
    "models.comments.comments_collection.insert_one",
    side_effect=Exception("DB insert failed"),
)
@patch("models.comments.CommentSchema")
@patch("models.comments.is_valid_object_id", return_value=True)
def test_create_comment_general_exception(mock_valid, mock_schema, mock_insert):
    result = create_comment(VALID_POST_ID, VALID_USER_ID, VALID_COMMENT_TEXT)
    assert result == "Error: DB insert failed"


@patch("models.comments.ObjectId", side_effect=InvalidId("bad object id"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_read_comment_invalid_objectid(mock_valid, mock_oid):
    result = read_comment("507f1f77bcf86cd799439011")
    assert result == "Error: Invalid ObjectId format."


@patch(
    "models.comments.comments_collection.find_one", side_effect=Exception("db exploded")
)
@patch("models.comments.is_valid_object_id", return_value=True)
def test_read_comment_general_exception(mock_valid, mock_find):
    result = read_comment("507f1f77bcf86cd799439011")
    assert result == "Error: db exploded"


@patch("models.comments.ObjectId", side_effect=InvalidId("bad object id"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_read_comment_field_invalid_objectid(mock_valid, mock_oid):
    result = read_comment_field("507f1f77bcf86cd799439011", "comment_text")
    assert result == "Error: Invalid ObjectId format."


@patch("models.comments.ObjectId", side_effect=InvalidId("bad object id"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_update_comment_invalid_objectid(mock_valid, mock_oid):
    result = update_comment("507f1f77bcf86cd799439011", "Updated comment")
    assert result == "Error: Invalid ObjectId format."


@patch(
    "models.comments.comments_collection.update_one",
    side_effect=Exception("Update failed"),
)
@patch("models.comments.is_valid_object_id", return_value=True)
def test_update_comment_general_exception(mock_valid, mock_update):
    result = update_comment("507f1f77bcf86cd799439011", "Updated comment")
    assert result == "Error: Update failed"


@patch("models.comments.ObjectId", side_effect=InvalidId("bad id"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_delete_comment_invalidid(mock_valid, mock_oid):
    result = delete_comment("507f1f77bcf86cd799439011")
    assert result == "Error: Invalid comment_id."


@patch("models.comments.ObjectId", side_effect=ValueError("value error"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_delete_comment_valueerror(mock_valid, mock_oid):
    result = delete_comment("507f1f77bcf86cd799439011")
    assert result == "Error: Invalid comment_id."


@patch("models.comments.ObjectId", side_effect=InvalidId("bad id"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_delete_comments_by_post_invalidid(mock_valid, mock_oid):
    result = delete_comments_by_post("507f1f77bcf86cd799439011")
    assert result == "Error: Invalid ObjectId format."


@patch("models.comments.ObjectId", side_effect=ValueError("bad input"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_delete_comments_by_post_valueerror(mock_valid, mock_oid):
    result = delete_comments_by_post("507f1f77bcf86cd799439011")
    assert result == "Error: Invalid ObjectId format."


@patch("models.comments.ObjectId", side_effect=InvalidId("bad id"))
@patch("models.comments.is_valid_object_id", return_value=True)
def test_get_all_comments_for_post_invalidid(mock_valid, mock_oid):
    result = get_all_comments_for_post("507f1f77bcf86cd799439011")
    assert result == "Error: Invalid ObjectId format."


def test_reply_to_comment_with_none_parent():
    result = reply_to_comment(
        post_id="507f1f77bcf86cd799439011",
        user_id="507f1f77bcf86cd799439012",
        comment_text="This is a reply",
        parent_comment_id=None,
    )
    assert result == "Error: parent_comment_id cannot be None for replies."
