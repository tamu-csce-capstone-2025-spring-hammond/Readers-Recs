import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime

import models.chat_messages as chat
from models.chat_messages import (
    create_chat_message,
    read_chat_message,
    read_chat_message_text,
    update_chat_message,
    delete_chat_message,
    get_all_chat_messages_for_book,
)


@pytest.fixture
def user_and_book():
    return str(ObjectId()), str(ObjectId())


def test_crud_chat_messages(user_and_book):
    uid, bid = user_and_book
    mid = str(ObjectId())

    with patch(
        "models.chat_messages.chat_messages_collection.insert_one",
        return_value=MagicMock(inserted_id=mid),
    ), patch(
        "models.chat_messages.chat_messages_collection.find_one",
        return_value={
            "_id": ObjectId(mid),
            "book_id": ObjectId(bid),
            "user_id": ObjectId(uid),
            "message_text": "Hello world",
            "date_posted": datetime.now(),
        },
    ), patch(
        "models.chat_messages.chat_messages_collection.update_one",
        return_value=MagicMock(matched_count=1),
    ), patch(
        "models.chat_messages.chat_messages_collection.delete_one",
        return_value=MagicMock(deleted_count=1),
    ), patch(
        "models.chat_messages.chat_messages_collection.find",
        return_value=[
            {
                "_id": ObjectId(mid),
                "book_id": ObjectId(bid),
                "user_id": ObjectId(uid),
                "message_text": "Hello world",
                "date_posted": datetime.now(),
            }
        ],
    ), patch(
        "models.chat_messages.is_valid_object_id", return_value=True
    ):

        # CREATE
        res = chat.create_chat_message(bid, uid, "Hello world")
        assert isinstance(res, str)

        # READ
        msg = chat.read_chat_message(res)
        assert msg["message_text"] == "Hello world"

        # TEXT
        assert chat.read_chat_message_text(res) == "Hello world"

        # UPDATE
        updated = chat.update_chat_message(res, "Updated message")
        assert isinstance(updated, dict)
        assert updated["message_text"] == "Hello world"  # mock doesn't change text

        # GET ALL
        msgs = chat.get_all_chat_messages_for_book(bid)
        assert isinstance(msgs, list)

        # DELETE
        deleted = chat.delete_chat_message(res)
        assert deleted == "Message deleted successfully."


def test_chat_message_error_paths(user_and_book):
    uid, bid = user_and_book
    mid = str(ObjectId())

    bad_id = "not_an_oid"
    fake_oid = str(ObjectId())

    def mock_is_valid_object_id(collection, oid):
        # Simulate missing user/doc for fake_oid
        return False if oid == fake_oid else True

    def mock_find_one(query):
        _id = query.get("_id")
        if _id == ObjectId(fake_oid):
            return None  # Simulate missing message
        return {
            "_id": ObjectId(mid),
            "book_id": ObjectId(bid),
            "user_id": ObjectId(uid),
            "message_text": "Hello world",
            "date_posted": "now",
        }

    with patch(
        "models.chat_messages.chat_messages_collection.insert_one",
        return_value=MagicMock(inserted_id=mid),
    ), patch(
        "models.chat_messages.chat_messages_collection.delete_one",
        return_value=MagicMock(deleted_count=0),
    ), patch(
        "models.chat_messages.chat_messages_collection.update_one",
        return_value=MagicMock(matched_count=0),
    ), patch(
        "models.chat_messages.chat_messages_collection.find_one",
        side_effect=mock_find_one,
    ), patch(
        "models.chat_messages.chat_messages_collection.find", return_value=[]
    ), patch(
        "models.chat_messages.is_valid_object_id", side_effect=mock_is_valid_object_id
    ):

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
    mid = str(ObjectId())

    with patch(
        "models.chat_messages.chat_messages_collection.insert_one",
        return_value=MagicMock(inserted_id=mid),
    ), patch(
        "models.chat_messages.chat_messages_collection.delete_one",
        return_value=MagicMock(deleted_count=1),
    ), patch(
        "models.chat_messages.is_valid_object_id", return_value=True
    ):

        result = create_chat_message(bid, uid, "Original message")
        assert isinstance(result, str)

        update_result = update_chat_message(result, "")
        assert update_result == "Error: Chat message must contain text."

        # Cleanup
        deletion = delete_chat_message(result)
        assert deletion == "Message deleted successfully."


def test_create_chat_message_invalid_book(user_and_book):
    uid, _ = user_and_book
    invalid_book_id = str(ObjectId())

    with patch(
        "models.chat_messages.is_valid_object_id",
        side_effect=lambda col, oid: col != "Books",
    ):
        result = create_chat_message(invalid_book_id, uid, "Message for bad book")
        assert result == "Error: Invalid book_id."
