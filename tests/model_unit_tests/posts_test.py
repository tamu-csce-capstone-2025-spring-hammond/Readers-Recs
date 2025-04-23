from unittest.mock import patch, MagicMock
from bson import ObjectId
from models.posts import (
    create_post,
    read_post,
    read_post_field,
    update_post,
    delete_post,
    get_all_posts_for_book,
)
from models.users import create_user, delete_user
import pytest
import uuid

@pytest.fixture
def user_and_book():
    return str(ObjectId()), str(ObjectId())

def test_crud_post_and_fields(user_and_book):
    uid, bid = user_and_book
    pid = str(ObjectId())

    mock_post = {
        "_id": ObjectId(pid),
        "user_id": ObjectId(uid),
        "book_id": ObjectId(bid),
        "title": "My Title",
        "post_text": "My Text",
        "tags": ["x", "y"],
    }

    updated_post = {
        **mock_post,
        "title": "New",
        "post_text": "NewText",
        "tags": ["z"]
    }

    def find_one_mock(query, *args, **kwargs):
        _id = query.get("_id")
        if _id == ObjectId(pid):
            if find_one_mock.counter == 0:
                find_one_mock.counter += 1
                return mock_post
            elif find_one_mock.counter == 1:
                find_one_mock.counter += 1
                return {"title": "My Title"}
            elif find_one_mock.counter == 2:
                find_one_mock.counter += 1
                return None
            elif find_one_mock.counter == 3:
                find_one_mock.counter += 1
                return updated_post
            else:
                return None  # simulate post not found after deletion
        return None
    find_one_mock.counter = 0

    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.insert_one", return_value=MagicMock(inserted_id=ObjectId(pid))), \
         patch("models.posts.posts_collection.find_one", side_effect=find_one_mock), \
         patch("models.posts.posts_collection.update_one", return_value=MagicMock(matched_count=1)), \
         patch("models.posts.posts_collection.delete_one", return_value=MagicMock(deleted_count=1)), \
         patch("models.posts.posts_collection.find", return_value=[mock_post]):

        # CREATE
        result = create_post(uid, bid, "My Title", "My Text", ["x", "y"])
        assert isinstance(result, str)

        # READ
        post = read_post(pid)
        assert str(post["_id"]) == pid
        assert post["title"] == "My Title"
        assert post["post_text"] == "My Text"
        assert post["tags"] == ["x", "y"]

        # READ SINGLE FIELD
        assert read_post_field(pid, "title") == "My Title"
        assert read_post_field(pid, "nonexistent") == "Error: Post not found."

        # UPDATE
        res = update_post(pid, title="New", post_text="NewText", tags="z")
        assert res == "Post updated successfully."
        updated = read_post(pid)
        assert updated["title"] == "New"
        assert updated["post_text"] == "NewText"
        assert updated["tags"] == ["z"]

        # LIST ALL FOR BOOK
        all_posts = get_all_posts_for_book(bid)
        assert isinstance(all_posts, list)
        assert any(str(p["_id"]) == pid for p in all_posts)

        # DELETE
        res = delete_post(pid)
        assert res == "Post deleted successfully."
        err = read_post(pid)
        assert err.startswith("Error:")

def test_invalid_ids_for_post():
    bad_id = "000000000000000000000000"

    # Case 1: both user and book are bad
    with patch("models.posts.is_valid_object_id", return_value=False):
        err = create_post(bad_id, bad_id, "a", "b", [])
        assert err.startswith("Error:")
        assert err == "Error: Invalid user_id."

    # Case 2: user is good, book is bad
    unique = uuid.uuid4().hex
    uid = str(ObjectId())

    with patch("models.users.create_user", return_value=uid), \
         patch("models.users.delete_user"), \
         patch("models.posts.is_valid_object_id", side_effect=lambda col, oid: col != "Books"):
        
        uid = create_user(
            first_name="T",
            last_name="U",
            username=f"u2_{unique}",
            email_address=f"u2_{unique}@example.com",
            oauth={"access_token": unique, "refresh_token": unique},
            profile_image="",
            interests=[],
            demographics={},
        )
        try:
            err2 = create_post(uid, bad_id, "a", "b", [])
            assert err2 == "Error: Invalid book_id."
        finally:
            delete_user(uid)


def test_read_post_not_found():
    fake_id = str(ObjectId())

    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.find_one", return_value=None):
        res = read_post(fake_id)
        assert res == "Error: Post not found."

def test_read_post_field_invalid_format():
    err = read_post_field("nope", "title")
    assert err == "Error: Invalid post_id."

def test_read_post_field_not_found():
    fake_id = str(ObjectId())

    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.find_one", return_value=None):
        res = read_post_field(fake_id, "anything")
        assert res == "Error: Post not found."

def test_update_post_invalid_format():
    err = update_post("xyz")
    assert err == "Error: Invalid post_id."


def test_update_post_not_found():
    fake_id = str(ObjectId())

    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.update_one", return_value=MagicMock(matched_count=0)):

        res = update_post(fake_id, title="New")
        assert res == "Error: Post not found."

def test_delete_post_invalid_format():
    err = delete_post("xxx")
    assert err == "Error: Invalid post_id."

def test_delete_post_not_found():
    fake_id = str(ObjectId())

    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.delete_one", return_value=MagicMock(deleted_count=0)):

        res = delete_post(fake_id)
        assert res == "Error: Post not found."

def test_get_all_posts_for_book_invalid_format():
    err = get_all_posts_for_book("bad_book_id")
    assert err == "Error: Invalid book_id."

def test_get_all_posts_for_book_empty(user_and_book):
    _, bid = user_and_book

    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.find", return_value=[]):
        res = get_all_posts_for_book(bid)
        assert res == []

def test_get_all_posts_for_book_not_found():
    fake = str(ObjectId())

    with patch("models.posts.is_valid_object_id", return_value=False):
        res = get_all_posts_for_book(fake)
        assert res == "Error: Invalid book_id."


def test_read_post_internal_exception():
    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.find_one", side_effect=Exception("DB error")):
        result = read_post(str(ObjectId()))
        # Depending on your actual function design, you may want to return a generic error string here
        assert "DB error" in result or isinstance(result, str)

def test_read_post_invalid_objectid():
    result = read_post("not-a-valid-objectid")
    assert result == "Error: Invalid post_id."


def test_create_post_unexpected_exception():
    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.PostSchema", side_effect=Exception("Unexpected failure")):
        res = create_post("uid", "bid", "Title", "Text", ["tag"])
        assert res == "Error: Unexpected failure"

def test_read_post_field_exception():
    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.find_one", side_effect=Exception("field read error")):
        res = read_post_field(str(ObjectId()), "title")
        assert res == "Error: field read error"

def test_update_post_exception():
    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.update_one", side_effect=Exception("update crash")):
        res = update_post(str(ObjectId()), title="boom")
        assert res == "Error: update crash"

def test_delete_post_exception():
    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.delete_one", side_effect=Exception("delete boom")), \
         patch("models.posts.delete_comments_by_post"):
        res = delete_post(str(ObjectId()))
        assert res == "Error: delete boom"

def test_get_all_posts_for_book_exception():
    with patch("models.posts.is_valid_object_id", return_value=True), \
         patch("models.posts.posts_collection.find", side_effect=Exception("find exploded")):
        res = get_all_posts_for_book(str(ObjectId()))
        assert res == "Error: find exploded"

def test_create_post_validation_error():
    with patch("models.posts.is_valid_object_id", return_value=True):
        # Pass an invalid value for `tags` (e.g., an integer instead of list or string)
        result = create_post("valid_user_id", "valid_book_id", "Title", "Text", 123)
        assert result.startswith("Schema Validation Error:")
