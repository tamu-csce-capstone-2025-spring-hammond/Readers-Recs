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


def test_create_read_update_delete_message(user_and_book):
    uid, bid = user_and_book

    mid = create_chat_message(bid, uid, "Hello world")
    assert isinstance(mid, str)

    msg = read_chat_message(mid)
    assert str(msg["_id"]) == mid
    assert msg["message_text"] == "Hello world"

    assert read_chat_message_text(mid) == "Hello world"

    update_result = update_chat_message(mid, "Updated message")
    assert isinstance(update_result, dict)
    assert update_result["message_text"] == "Updated message"

    all_msgs = get_all_chat_messages_for_book(bid)
    assert any(str(m["_id"]) == mid for m in all_msgs)

    delete_result = delete_chat_message(mid)
    assert delete_result == "Message deleted successfully."
    deleted = read_chat_message(mid)
    assert deleted in ["Message not found.", "Error: Invalid message_id."]


def test_chat_message_exceptions():
    bad_id = "bad"
    fake_id = str(ObjectId())

    assert create_chat_message(bad_id, bad_id, "msg").startswith("Error:")

    # invalid inputs
    assert create_chat_message(fake_id, fake_id, None).startswith("Error:")
    assert create_chat_message(fake_id, fake_id, 123).startswith("Error:")
    assert create_chat_message(fake_id, fake_id, {}).startswith("Error:")
    assert create_chat_message(fake_id, fake_id, "").startswith("Error:")

    assert read_chat_message(bad_id).startswith("Error:")
    result = read_chat_message(fake_id)
    assert result in ["Message not found.", "Error: Invalid message_id."]

    assert read_chat_message_text(bad_id).startswith("Error:")
    assert read_chat_message_text(fake_id) in [
        "Message not found.",
        "Error: Invalid message_id.",
    ]

    assert update_chat_message(bad_id, "text").startswith("Error:")

    # empty update text
    update_result = update_chat_message(fake_id, "")
    assert update_result in [
        "Message not found.",
        "Error: Invalid message_id.",
        "Error: message_text must be a non-empty string.",
    ]

    assert delete_chat_message(bad_id).startswith("Error:")
    assert delete_chat_message(fake_id) in [
        "Message not found.",
        "Error: Invalid message_id.",
    ]

    assert get_all_chat_messages_for_book(bad_id).startswith("Error:")
    assert get_all_chat_messages_for_book(fake_id) == []
