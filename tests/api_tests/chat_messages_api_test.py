import pytest
from main import app
import uuid
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.user_bookshelf import create_user_bookshelf, delete_user_bookshelf

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user_and_book():
    u = uuid.uuid4().hex
    user_id = create_user(
        first_name="Chat",
        last_name="User",
        username=f"chatuser_{u}",
        email_address=f"{u}@test.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    book_id = create_book(
        title="Chat Book",
        author=["Author"],
        page_count=300,
        genre="Fiction",
        tags=["chat"],
        publication_date="2024-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="ChatPub",
        summary="Summary",
        genre_tags=["fiction"],
    )

    from datetime import datetime

    create_user_bookshelf(
        user_id, book_id, status="read", date_finished=datetime(2024, 1, 15)
    )

    yield user_id, book_id

    delete_user_bookshelf(user_id, book_id)
    delete_user(user_id)
    delete_book(book_id)


def test_get_chat_messages_invalid_book(client):
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

    response = client.post(
        f"/api/chat/{book_id}/send",
        json={"user_id": user_id, "message_text": "This is a chat message!"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message_id" in data


def test_get_chat_messages_valid(client, valid_user_and_book):
    user_id, book_id = valid_user_and_book

    # Send a message
    client.post(
        f"/api/chat/{book_id}/send", json={"user_id": user_id, "message_text": "Hello!"}
    )

    response = client.get(f"/api/chat/{book_id}/messages")
    assert response.status_code == 200
    messages = response.get_json()
    assert isinstance(messages, list)
    assert any(msg["message_text"] == "Hello!" for msg in messages)


def test_get_last_read_book_valid(client, valid_user_and_book):
    user_id, _ = valid_user_and_book
    response = client.get(f"/api/chat/user/{user_id}/lastread")
    assert response.status_code == 200
    data = response.get_json()
    assert "title" in data
    assert "rating" in data


def test_send_chat_message_internal_error(monkeypatch, client, valid_user_and_book):
    from api import chat_messages

    def crash(*args, **kwargs):
        raise Exception("send error")

    monkeypatch.setattr("api.chat_messages.create_chat_message", crash)

    user_id, book_id = valid_user_and_book
    response = client.post(
        f"/api/chat/{book_id}/send", json={"user_id": user_id, "message_text": "Boom"}
    )
    assert response.status_code == 500
    assert "send error" in response.get_json()["error"]


def test_get_chat_messages_internal_error(monkeypatch, client, valid_user_and_book):
    from api import chat_messages

    def crash(_):
        raise Exception("fetch crash")

    monkeypatch.setattr("api.chat_messages.get_all_chat_messages_for_book", crash)

    _, book_id = valid_user_and_book
    response = client.get(f"/api/chat/{book_id}/messages")
    assert response.status_code == 500
    assert "fetch crash" in response.get_json()["error"]


def test_get_last_read_book_internal_error(monkeypatch, client, valid_user_and_book):
    from api import chat_messages

    def boom(_):
        raise Exception("lastread error")

    monkeypatch.setattr("api.chat_messages.get_read_books", boom)

    user_id, _ = valid_user_and_book
    response = client.get(f"/api/chat/user/{user_id}/lastread")
    assert response.status_code == 500
    assert "lastread error" in response.get_json()["error"]


def test_get_last_read_book_no_finish_date(client):
    from models.users import create_user, delete_user
    from models.books import create_book, delete_book
    from models.user_bookshelf import create_user_bookshelf, delete_user_bookshelf

    import uuid

    u = uuid.uuid4().hex

    user_id = create_user(
        first_name="NoFinish",
        last_name="User",
        username=f"nofinish_{u}",
        email_address=f"{u}@test.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    book_id = create_book(
        title="Unfinished Book",
        author=["Author"],
        page_count=111,
        genre="Mystery",
        tags=[],
        publication_date="2024-02-02",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="MysteryPub",
        summary="Mystery",
        genre_tags=["mystery"],
    )

    # add with status=read but no date_finished
    create_user_bookshelf(user_id, book_id, status="read")

    response = client.get(f"/api/chat/user/{user_id}/lastread")
    assert response.status_code == 404
    assert response.get_json()["message"] == "No books marked as read yet."

    delete_user_bookshelf(user_id, book_id)
    delete_user(user_id)
    delete_book(book_id)


def test_get_last_read_book_no_finish_date(client):
    from models.users import create_user, delete_user
    from models.books import create_book, delete_book
    from models.user_bookshelf import create_user_bookshelf, delete_user_bookshelf

    import uuid

    u = uuid.uuid4().hex

    user_id = create_user(
        first_name="NoFinish",
        last_name="User",
        username=f"nofinish_{u}",
        email_address=f"{u}@test.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    book_id = create_book(
        title="Unfinished Book",
        author=["Author"],
        page_count=111,
        genre="Mystery",
        tags=[],
        publication_date="2024-02-02",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="MysteryPub",
        summary="Mystery",
        genre_tags=["mystery"],
    )

    # add with status=read but no date_finished
    create_user_bookshelf(user_id, book_id, status="read")

    response = client.get(f"/api/chat/user/{user_id}/lastread")
    assert response.status_code == 404
    assert response.get_json()["message"] == "No books marked as read yet."

    delete_user_bookshelf(user_id, book_id)
    delete_user(user_id)
    delete_book(book_id)
