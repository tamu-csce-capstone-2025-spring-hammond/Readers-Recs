import pytest
from unittest.mock import patch
from main import app
from bson import ObjectId
from datetime import datetime
import pytz
from api.chat_messages import parse_date

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user_and_book():
    fake_user_id = str(ObjectId())
    fake_book_id = str(ObjectId())

    with patch("models.users.create_user", return_value=fake_user_id), patch(
        "models.books.create_book", return_value=fake_book_id
    ), patch(
        "models.user_bookshelf.create_user_bookshelf", return_value=str(ObjectId())
    ), patch(
        "models.user_bookshelf.delete_user_bookshelf"
    ), patch(
        "models.users.delete_user"
    ), patch(
        "models.books.delete_book"
    ):

        yield fake_user_id, fake_book_id


def test_get_chat_messages_invalid_book(client):
    with patch(
        "models.chat_messages.get_all_chat_messages_for_book",
        return_value="Error: Invalid book_id.",
    ):
        response = client.get("/api/chat/invalid_id/messages")
        assert response.status_code in [400, 500]
        assert "error" in response.get_json()


def test_send_chat_message_missing_fields(client):
    response = client.post("/api/chat/invalid_id/send", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_send_chat_message_invalid_user_id(client):
    response = client.post(
        "/api/chat/invalid_id/send",
        json={"user_id": "baduser", "message_text": "hello"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_send_chat_message_empty_text(client):
    response = client.post(
        "/api/chat/invalid_id/send",
        json={"user_id": "000000000000000000000000", "message_text": ""},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_last_read_book_invalid_user(client):
    response = client.get("/api/chat/user/invalid_user/lastread")
    assert response.status_code in [400, 404, 500]


def test_send_chat_message_valid(client, valid_user_and_book):
    user_id, book_id = valid_user_and_book
    fake_message_id = str(ObjectId())

    with patch("api.chat_messages.create_chat_message", return_value=fake_message_id):
        response = client.post(
            f"/api/chat/{book_id}/send",
            json={"user_id": user_id, "message_text": "This is a chat message!"},
        )

    assert response.status_code == 201
    data = response.get_json()
    assert "message_id" in data
    assert data["message_id"] == fake_message_id


def test_get_chat_messages_valid(client, valid_user_and_book):
    user_id, book_id = valid_user_and_book
    mock_message = {
        "_id": str(ObjectId()),
        "book_id": book_id,
        "user_id": user_id,
        "message_text": "Hello!",
        "username": "mockuser",
        "profile_image": "",
    }

    # Patch where the route *uses* the functions
    with patch(
        "api.chat_messages.create_chat_message", return_value=str(ObjectId())
    ), patch(
        "api.chat_messages.get_all_chat_messages_for_book", return_value=[mock_message]
    ):
        client.post(
            f"/api/chat/{book_id}/send",
            json={"user_id": user_id, "message_text": "Hello!"},
        )
        response = client.get(f"/api/chat/{book_id}/messages")

    assert response.status_code == 200
    messages = response.get_json()
    assert isinstance(messages, list)
    assert any(msg["message_text"] == "Hello!" for msg in messages)


def test_get_last_read_book_valid(client, valid_user_and_book):
    user_id, book_id = valid_user_and_book

    mock_read_books = [
        {
            "user_id": user_id,
            "book_id": book_id,
            "title": "Mock Book",
            "rating": "pos",
            "status": "read",
            "date_finished": datetime(2024, 1, 1),
        }
    ]

    mock_book_details = {
        "_id": ObjectId(),
        "title": "Mock Book",
        "author": ["Test Author"],
        "page_count": 123,
        "genre": "Test Genre",
        "tags": ["fiction"],
        "publication_date": datetime(2023, 1, 1),
        "isbn": "000000000",
        "isbn13": "0000000000000",
        "cover_image": "",
        "language": "en",
        "publisher": "TestPub",
        "summary": "A great book",
        "genre_tags": ["fiction"],
        "embedding": [],
    }

    with patch("api.chat_messages.get_read_books", return_value=mock_read_books), patch(
        "api.chat_messages.read_book_by_bookId", return_value=mock_book_details
    ):
        response = client.get(f"/api/chat/user/{user_id}/lastread")

    assert response.status_code == 200
    data = response.get_json()
    assert "title" in data
    assert "rating" in data


def test_send_chat_message_internal_error(monkeypatch, client, valid_user_and_book):
    user_id, book_id = valid_user_and_book

    def crash(*args, **kwargs):
        raise Exception("send error")

    # Patch where create_chat_message is *used* in your route
    monkeypatch.setattr("api.chat_messages.create_chat_message", crash)

    response = client.post(
        f"/api/chat/{book_id}/send",
        json={"user_id": user_id, "message_text": "Boom"},
    )
    assert response.status_code == 500
    assert "send error" in response.get_json()["error"]


def test_get_last_read_book_internal_error(monkeypatch, client, valid_user_and_book):
    user_id, _ = valid_user_and_book

    def boom(_):
        raise Exception("lastread error")

    monkeypatch.setattr("api.chat_messages.get_read_books", boom)

    response = client.get(f"/api/chat/user/{user_id}/lastread")
    assert response.status_code == 500
    assert "lastread error" in response.get_json()["error"]


def test_get_chat_messages_for_book_exception(client):
    book_id = str(ObjectId())

    def raise_error(_):
        raise Exception("simulated internal error")

    with patch(
        "api.chat_messages.get_all_chat_messages_for_book", side_effect=raise_error
    ):
        response = client.get(f"/api/chat/{book_id}/messages")

    assert response.status_code == 500
    assert "simulated internal error" in response.get_json()["error"]


def test_get_last_read_book_no_books_finished(client):
    user_id = str(ObjectId())

    # All entries are missing a date_finished, should return 404
    mock_read_books = [
        {
            "user_id": user_id,
            "book_id": str(ObjectId()),
            "title": "Unread Book",
            "rating": "mid",
            "status": "read",
            "date_finished": None,
        }
    ]

    with patch("api.chat_messages.get_read_books", return_value=mock_read_books):
        response = client.get(f"/api/chat/user/{user_id}/lastread")

    assert response.status_code == 404
    assert response.get_json()["message"] == "No books marked as read yet."


def test_parse_date_naive_datetime():
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    result = parse_date(naive_dt)
    assert result.tzinfo.zone == "US/Central"
    assert result.hour == 12


def test_parse_date_aware_datetime():
    aware = pytz.timezone("US/Central").localize(datetime(2024, 1, 1, 12, 0, 0))
    result = parse_date(aware)
    assert result is aware


def test_parse_date_naive_string():
    result = parse_date("2024-01-01T12:00:00")
    assert result.tzinfo.zone == "US/Central"
    assert result.hour == 12


def test_parse_date_invalid_string():
    result = parse_date("not-a-date")
    assert result.year == 1
    assert result.tzinfo.zone == "US/Central"


def test_parse_date_none_input():
    result = parse_date(None)
    assert result.year == 1
    assert result.tzinfo.zone == "US/Central"


def test_parse_date_int_input():
    result = parse_date(12345)
    assert result.year == 1
    assert result.tzinfo.zone == "US/Central"
