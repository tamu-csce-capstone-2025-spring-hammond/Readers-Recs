import pytest
import uuid
from bson import ObjectId

from backend.models.chat_messages import (
    create_chat_message,
    read_chat_message,
    read_chat_message_text,
    update_chat_message,
    delete_chat_message,
    get_all_chat_messages_for_book,
)
from backend.models.users import create_user, delete_user
from backend.models.books import create_book, delete_book


@pytest.fixture
def user_and_book():
    """Create a unique user and book, then clean up afterward."""
    u = uuid.uuid4().hex
    uid = create_user(
        first_name="Test",
        last_name="User",
        username=f"chatuser_{u}",
        email_address=f"chat_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="ChatBook",
        author=["Author"],
        page_count=200,
        genre="Fiction",
        tags=["chat"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["fiction"],
    )
    yield uid, bid
    delete_user(uid)
    delete_book(bid)


def test_crud_chat_messages(user_and_book):
    """Test basic create / read / update / delete cycle."""
    uid, bid = user_and_book

    # CREATE
    mid = create_chat_message(bid, uid, "Hello world")
    assert isinstance(mid, str)

    # READ full document
    msg = read_chat_message(mid)
    assert str(msg["_id"]) == mid
    assert msg["message_text"] == "Hello world"

    # READ just the text
    assert read_chat_message_text(mid) == "Hello world"

    # UPDATE
    updated = update_chat_message(mid, "Updated message")
    assert isinstance(updated, dict)
    assert updated["message_text"] == "Updated message"

    # LIST for book
    all_msgs = get_all_chat_messages_for_book(bid)
    assert any(str(m["_id"]) == mid for m in all_msgs)

    # DELETE
    res = delete_chat_message(mid)
    assert res == "Message deleted successfully."
    after = read_chat_message(mid)
    assert after in ["Message not found.", "Error: Invalid message_id."]


def test_chat_message_error_paths(user_and_book):
    """Test all the exception / invalid-input branches."""
    uid, bid = user_and_book

    bad_id = "not_an_oid"
    fake_oid = str(ObjectId())

    # CREATE errors
    assert create_chat_message(bad_id, bad_id, "msg").startswith("Error:")
    assert create_chat_message(bid, fake_oid, "msg").startswith("Error:")
    for bad_text in (None, 123, {}, ""):
        assert create_chat_message(bid, uid, bad_text).startswith("Error:")

    # READ errors
    assert read_chat_message(bad_id).startswith("Error:")
    r = read_chat_message(fake_oid)
    assert r in ["Message not found.", "Error: Invalid message_id."]

    assert read_chat_message_text(bad_id).startswith("Error:")
    rt = read_chat_message_text(fake_oid)
    assert rt in ["Message not found.", "Error: Invalid message_id."]

    # UPDATE errors
    assert update_chat_message(bad_id, "text").startswith("Error:")
    empty_res = update_chat_message(fake_oid, "")
    assert empty_res in [
        "Message not found.",
        "Error: Invalid message_id.",
        "Error: Chat message must contain text.",
    ]

    # DELETE errors
    assert delete_chat_message(bad_id).startswith("Error:")
    d = delete_chat_message(fake_oid)
    assert d in ["Message not found.", "Error: Invalid message_id."]

    # GET ALL for bad book
    assert get_all_chat_messages_for_book(bad_id).startswith("Error:")
    assert get_all_chat_messages_for_book(fake_oid) == []


def test_update_chat_message_empty_input(user_and_book):
    uid, bid = user_and_book

    # Create a valid message first
    mid = create_chat_message(bid, uid, "Original message")
    assert isinstance(mid, str)

    # Now try to update it with an empty string
    result = update_chat_message(mid, "")
    assert result == "Error: Chat message must contain text."

    # Cleanup
    delete_chat_message(mid)


def test_create_chat_message_invalid_book(user_and_book):
    uid, _ = user_and_book
    invalid_book_id = ObjectId()

    result = create_chat_message(invalid_book_id, uid, "Message for bad book")
    assert result == "Error: Invalid book_id."
