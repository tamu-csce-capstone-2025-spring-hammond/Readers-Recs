import pytest
import uuid
from bson import ObjectId
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.user_bookshelf import delete_user_bookshelf
from main import app
from api.bookshelf import parse_date
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def user_and_book():
    uid = uuid.uuid4().hex
    user_id = create_user(
        first_name="T",
        last_name="User",
        username=f"testuser_{uid}",
        email_address=f"{uid}@example.com",
        oauth={"access_token": uid, "refresh_token": uid},
        profile_image="",
        interests=[],
        demographics={"age": 21}
    )
    book_id = create_book(
        title="Test Book",
        author=["Author"],
        page_count=123,
        genre="Test",
        tags=["sample"],
        publication_date="2025-01-01",
        isbn=uid[:9],
        isbn13=uid[:13],
        cover_image="",
        language="en",
        publisher="Publisher",
        summary="Summary",
        genre_tags=["test"]
    )
    yield user_id, book_id
    delete_user_bookshelf(user_id, book_id)
    delete_user(user_id)
    delete_book(book_id)

def test_add_book_to_bookshelf(client, user_and_book):
    uid, bid = user_and_book
    res = client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "pos"
    })
    assert res.status_code == 201
    assert "Book added to bookshelf" in res.get_json()["message"]

def test_get_read_books(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "pos"
    })
    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_get_unread_books(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "to-read",
        "rating": "mid"
    })
    res = client.get(f"/shelf/api/user/{uid}/books/to-read")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_get_currently_reading_books(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "currently-reading",
        "rating": "mid"
    })
    res = client.get(f"/shelf/api/user/{uid}/books/currently-reading")
    assert res.status_code == 200
    assert "title" in res.get_json()

def test_update_and_get_page_number(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "currently-reading",
        "rating": "mid"
    })
    update = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page", json={"page_number": 42})
    assert update.status_code == 200
    get = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page")
    assert get.status_code == 200
    assert get.get_json()["page_number"] == 42

def test_update_bookshelf_status(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "to-read",
        "rating": "mid"
    })
    update = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/status", json={"status": "read"})
    assert update.status_code == 200
    assert "Book status updated" in update.get_json()["message"]

def test_rate_book_api(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "mid"
    })
    res = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/rating", json={"rating": "pos"})
    assert res.status_code == 200
    assert "Book rating updated" in res.get_json()["message"]

def test_delete_book_from_bookshelf(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "mid"
    })
    res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
    assert res.status_code == 200
    assert "Book deleted" in res.get_json()["message"]

def test_get_book_status(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "mid"
    })
    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/status")
    assert res.status_code == 200
    assert res.get_json()["status"] == "read"

def test_get_last_read_book(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "pos"
    })
    res = client.get(f"/shelf/api/user/{uid}/books/lastread")
    assert res.status_code == 200
    assert res.get_json()["rating"] == "pos"


def test_add_book_missing_fields(client, user_and_book):
    uid, bid = user_and_book
    res = client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid)
        # missing 'status' and 'rating'
    })
    assert res.status_code == 500  # Internal error due to KeyError (consider handling in your route)

def test_update_page_invalid_page_number(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "currently-reading",
        "rating": "mid"
    })
    res = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page", json={"page_number": -10})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid page number"

def test_rate_book_invalid_rating(client, user_and_book):
    uid, bid = user_and_book
    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "mid"
    })
    res = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/rating", json={"rating": "amazing"})
    assert res.status_code == 400
    assert "Invalid rating" in res.get_json()["error"]

def test_get_status_invalid_book_id(client, user_and_book):
    uid, _ = user_and_book
    res = client.get(f"/shelf/api/user/{uid}/bookshelf/notanid/status")
    assert res.status_code == 400

def test_get_current_page_no_entry(client, user_and_book):
    uid, bid = user_and_book
    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page")
    assert res.status_code == 404
    assert "UserBookshelf entry not found" in res.get_json()["error"]

def test_get_read_books_db_error(client, monkeypatch, user_and_book):
    uid, _ = user_and_book

    def boom(*args, **kwargs):
        raise Exception("Mongo exploded")

    monkeypatch.setattr("api.bookshelf.get_read_books", boom)

    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 500
    assert "Mongo exploded" in res.get_json()["error"]

def test_get_last_read_book_boom(client, monkeypatch, user_and_book):
    uid, _ = user_and_book

    def boom(uid):
        raise Exception("BOOM in get_read_books")

    monkeypatch.setattr("api.bookshelf.get_read_books", boom)


    res = client.get(f"/shelf/api/user/{uid}/books/lastread")
    assert res.status_code == 500
    assert "BOOM in get_read_books" in res.get_json()["error"]

def test_update_page_number_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "currently-reading",
        "rating": "mid"
    })

    def crash(user_id, book_id, new_page):
        raise Exception("Mongo fell down")

    monkeypatch.setattr("api.bookshelf.update_page_number", crash)

    res = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page", json={"page_number": 25})
    assert res.status_code == 500
    assert "Mongo fell down" in res.get_json()["error"]

def test_rate_book_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "mid"
    })

    def boom(*args, **kwargs):
        raise Exception("Kaboom in rate_book")

    monkeypatch.setattr("api.bookshelf.rate_book", boom)

    res = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/rating", json={"rating": "pos"})
    assert res.status_code == 500
    assert "Kaboom in rate_book" in res.get_json()["error"]

def test_parse_date_valid_string():
    iso_str = "2024-04-21T10:30:00"
    parsed = parse_date(iso_str)
    assert isinstance(parsed, datetime)
    assert parsed.year == 2024
    assert parsed.month == 4
    assert parsed.day == 21

def test_parse_date_datetime_input():
    now = datetime.now()
    result = parse_date(now)
    assert result is now  # should return same object

def test_parse_date_invalid_string():
    result = parse_date("not-a-date")
    assert result == datetime.min

def test_parse_date_none():
    result = parse_date(None)
    assert result == datetime.min

def test_parse_date_number():
    result = parse_date(123456)
    assert result == datetime.min

def test_get_currently_reading_books_crash(client, monkeypatch, user_and_book):
    uid, _ = user_and_book

    def boom(*args, **kwargs):
        raise Exception("DB crash in get_currently_reading_books")

    monkeypatch.setattr("api.bookshelf.get_currently_reading_books", boom)

    res = client.get(f"/shelf/api/user/{uid}/books/currently-reading")
    assert res.status_code == 500
    assert "DB crash in get_currently_reading_books" in res.get_json()["error"]

def test_get_current_page_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    def explode(*args, **kwargs):
        raise Exception("Boom in get_page_number")

    monkeypatch.setattr("api.bookshelf.get_page_number", explode)

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page")
    assert res.status_code == 500
    assert "Boom in get_page_number" in res.get_json()["error"]

def test_get_unread_books_crash(client, monkeypatch, user_and_book):
    uid, _ = user_and_book

    def explode(*_):
        raise Exception("Kaboom in get_unread_books")

    monkeypatch.setattr("api.bookshelf.get_unread_books", explode)

    res = client.get(f"/shelf/api/user/{uid}/books/to-read")
    assert res.status_code == 500
    assert "Kaboom in get_unread_books" in res.get_json()["error"]

def test_add_book_to_bookshelf_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    def explode(*args, **kwargs):
        raise Exception("Explosion in create_user_bookshelf")

    monkeypatch.setattr("api.bookshelf.create_user_bookshelf", explode)

    res = client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "read",
        "rating": "mid"
    })
    assert res.status_code == 500
    assert "Explosion in create_user_bookshelf" in res.get_json()["error"]

def test_update_bookshelf_status_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    client.post(f"/shelf/api/user/{uid}/bookshelf", json={
        "book_id": str(bid),
        "status": "to-read",
        "rating": "mid"
    })

    def boom(*args, **kwargs):
        raise Exception("Status update error")

    monkeypatch.setattr("api.bookshelf.update_user_bookshelf_status", boom)

    res = client.put(f"/shelf/api/user/{uid}/bookshelf/{bid}/status", json={"status": "read"})
    assert res.status_code == 500
    assert "Status update error" in res.get_json()["error"]

def test_delete_bookshelf_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    def boom(*_):
        raise Exception("Delete blew up")

    monkeypatch.setattr("api.bookshelf.delete_user_bookshelf", boom)

    res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
    assert res.status_code == 500
    assert "Delete blew up" in res.get_json()["error"]

def test_get_book_status_crash(client, monkeypatch, user_and_book):
    uid, bid = user_and_book

    def boom(*_):
        raise Exception("Status fetch exploded")

    monkeypatch.setattr("api.bookshelf.get_bookshelf_status", boom)

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/status")
    assert res.status_code == 500
    assert "Status fetch exploded" in res.get_json()["error"]
