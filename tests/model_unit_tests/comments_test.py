import pytest
import uuid
from bson import ObjectId
from bson.errors import InvalidId
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
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.posts import create_post, delete_post


@pytest.fixture
def user_post():
    u = uuid.uuid4().hex
    uid = create_user(
        first_name="T",
        last_name="U",
        username=f"testuser_{u}",
        email_address=f"test_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="CommentTest",
        author=["Author"],
        page_count=100,
        genre="Fiction",
        tags=["test"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["fiction"],
    )
    pid = create_post(uid, bid, "Post Title", "Post Content", ["tag"])
    yield uid, bid, pid
    delete_post(pid)
    delete_user(uid)
    delete_book(bid)


def test_create_read_update_delete_comment(user_post):
    uid, _, pid = user_post

    cid = create_initial_comment(pid, uid, "This is a comment")
    assert isinstance(cid, str)

    comment = read_comment(cid)
    assert str(comment["_id"]) == cid
    assert comment["comment_text"] == "This is a comment"

    assert read_comment_field(cid, "comment_text") == "This is a comment"

    assert update_comment(cid, "Updated text") == "Comment updated successfully."
    updated = read_comment(cid)
    assert updated["comment_text"] == "Updated text"

    assert delete_comment(cid) == "Comment deleted successfully."
    deleted_result = read_comment(cid)
    assert deleted_result in [
        "Comment not found.",
        "Error: Invalid ObjectId format.",
        "Error: Invalid comment_id.",
    ]


def test_create_comment_invalid_parent_id(user_post):
    uid, _, pid = user_post
    bad_parent = "notarealid"

    result = create_comment(pid, uid, "Reply", parent_comment_id=bad_parent)
    assert result == "Error: Invalid ObjectId format."


def test_create_comment_schema_validation_error(user_post):
    uid, _, pid = user_post

    result = create_comment(pid, uid, None)  # Missing comment_text
    assert result.startswith("Schema Validation Error:")


def test_nested_comments(user_post):
    uid, _, pid = user_post

    parent_id = create_initial_comment(pid, uid, "Parent")
    reply_id = reply_to_comment(pid, uid, "Child reply", parent_id)

    all_comments = get_all_comments_for_post(pid)
    parent = next((c for c in all_comments if str(c["_id"]) == parent_id), None)
    assert parent is not None
    assert "replies" in parent
    assert any(str(r["_id"]) == reply_id for r in parent["replies"])

    delete_comment(reply_id)
    delete_comment(parent_id)


def test_comment_exceptions():
    bad_id = "bad"
    fake_id = ObjectId("000000000000000000000000")

    assert create_comment(bad_id, bad_id, "text").startswith("Error:")
    result = create_comment(fake_id, bad_id, "text")
    assert result in ["Error: Invalid user_id.", "Error: Invalid post_id."]
    result = create_comment(fake_id, fake_id, "text", parent_comment_id=bad_id)
    assert result in ["Error: Invalid parent_comment_id.", "Error: Invalid post_id."]

    # schema validation errors
    result = create_comment(fake_id, fake_id, None)
    assert result.startswith("Schema Validation Error:") or result.startswith("Error:")
    assert create_comment(
        fake_id, fake_id, "Valid", parent_comment_id=[123]
    ).startswith("Error:")

    assert read_comment(bad_id).startswith("Error:")
    read_result = read_comment(fake_id)
    assert read_result in ["Comment not found.", "Error: Invalid comment_id."]

    assert read_comment_field(bad_id, "comment_text").startswith("Error:")
    read_field_result = read_comment_field(fake_id, "comment_text")
    assert read_field_result in [
        "Comment not found.",
        "Error: Invalid comment_id.",
        "Field 'comment_text' not found in comment.",
    ]

    nonexistent_field_result = read_comment_field(fake_id, "nonexistent_field")
    assert nonexistent_field_result in [
        "Field 'nonexistent_field' not found in comment.",
        "Error: Invalid comment_id.",
    ]

    assert update_comment(bad_id, "new").startswith("Error:")
    update_result = update_comment(fake_id, "new")
    assert update_result in ["Comment not found.", "Error: Invalid comment_id."]

    assert delete_comment(bad_id).startswith("Error:")
    assert delete_comment(fake_id) in [
        "Comment not found.",
        "Error: Invalid comment_id.",
    ]

    assert delete_comments_by_post(bad_id).startswith("Error:")
    assert delete_comments_by_post(fake_id) in [
        "Error: Invalid post_id.",
        "No comments found for this post.",
    ]


def test_get_all_comments_for_post_invalid():
    result = get_all_comments_for_post("bad")
    assert result in ["Error: Invalid ObjectId format.", "Error: Invalid post_id."]


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


def test_read_comment_field_not_found(user_post):
    uid, _, pid = user_post
    cid = create_initial_comment(pid, uid, "This is fine.")

    result = read_comment_field(cid, "not_a_real_field")
    assert result == "Field 'not_a_real_field' not found in comment."

    delete_comment(cid)


def test_update_comment_not_found():
    fake = str(ObjectId())
    result = update_comment(fake, "new content")
    assert result == "Error: Invalid comment_id."


def test_delete_comment_not_found():
    fake = str(ObjectId())
    result = delete_comment(fake)
    assert result == "Error: Invalid comment_id."
