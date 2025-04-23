import uuid
from bson import ObjectId
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.user_bookshelf import delete_user_bookshelf
from main import app
from api.bookshelf import parse_date, objectid_to_str
from datetime import datetime
from unittest.mock import patch, MagicMock
from flask import Flask
import pytest


@pytest.fixture
def client():
    from main import app

    app.config["TESTING"] = True
    return app.test_client()


VALID_USER_ID = "507f1f77bcf86cd799439011"
VALID_BOOK_ID = "507f1f77bcf86cd799439012"


@pytest.fixture
def user_and_book():
    return VALID_USER_ID, VALID_BOOK_ID


@patch("api.bookshelf.get_read_books")
def test_get_read_books(mock_get_read_books, client, user_and_book):
    uid, _ = user_and_book

    mock_get_read_books.return_value = [
        {"book_id": "507f1f77bcf86cd799439012", "status": "read"}
    ]

    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
    mock_get_read_books.assert_called_once_with(uid)


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_unread_books")
def test_get_unread_books(mock_get_unread_books, mock_read_book, client, user_and_book):
    uid, _ = user_and_book

    mock_get_unread_books.return_value = [{"book_id": "507f1f77bcf86cd799439013"}]
    mock_read_book.return_value = {
        "title": "Unread Book",
        "book_id": "507f1f77bcf86cd799439013",
    }

    res = client.get(f"/shelf/api/user/{uid}/books/to-read")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
    mock_get_unread_books.assert_called_once_with(uid)


def test_objectid_to_str_valid():
    oid = ObjectId()
    result = objectid_to_str(oid)
    assert isinstance(result, str)
    assert result == str(oid)


def test_objectid_to_str_invalid_type():
    with pytest.raises(TypeError) as excinfo:
        objectid_to_str("not-an-objectid")
    assert "is not ObjectId" in str(excinfo.value)


def test_parse_date_with_datetime():
    now = datetime.now()
    assert parse_date(now) is now  # Should return original datetime object


def test_parse_date_with_iso_string():
    date_str = "2025-04-23T10:30:00"
    result = parse_date(date_str)
    assert isinstance(result, datetime)
    assert result.year == 2025 and result.month == 4 and result.day == 23


def test_parse_date_with_invalid_string():
    result = parse_date("not-a-date")
    assert result == datetime.min


def test_parse_date_with_none():
    result = parse_date(None)
    assert result == datetime.min


def test_parse_date_with_integer():
    result = parse_date(12345)
    assert result == datetime.min


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_read_books")
def test_get_last_read_book_success(mock_get_books, mock_read_book, client):
    user_id = "507f1f77bcf86cd799439011"

    # Mock books with valid finish date and ObjectId
    fake_oid = ObjectId()
    mock_get_books.return_value = [
        {
            "book_id": "507f1f77bcf86cd799439012",
            "date_finished": "2025-04-22T12:00:00",
            "_id": fake_oid,
            "rating": "pos",
        }
    ]
    mock_read_book.return_value = {
        "title": "Test Book",
        "book_id": "507f1f77bcf86cd799439012",
    }

    res = client.get(f"/shelf/api/user/{user_id}/books/lastread")
    assert res.status_code == 200
    assert res.get_json()["rating"] == "pos"
    assert res.get_json()["title"] == "Test Book"


@patch("api.bookshelf.get_read_books", return_value=[])
def test_get_last_read_book_empty(mock_get_books, client):
    res = client.get("/shelf/api/user/507f1f77bcf86cd799439011/books/lastread")
    assert res.status_code == 404
    assert res.get_json()["message"] == "No books finished yet."


@patch("api.bookshelf.get_read_books", return_value="Error: Invalid user_id")
def test_get_last_read_book_returns_error_string(mock_get_books, client):
    res = client.get("/shelf/api/user/507f1f77bcf86cd799439011/books/lastread")
    assert res.status_code == 400
    assert res.get_json()["error"] == "Error: Invalid user_id"


@patch("api.bookshelf.get_read_books", side_effect=Exception("Crash"))
def test_get_last_read_book_crashes(mock_get_books, client):
    res = client.get("/shelf/api/user/507f1f77bcf86cd799439011/books/lastread")
    assert res.status_code == 500
    assert "Crash" in res.get_json()["error"]


@patch("api.bookshelf.read_book_by_bookId", return_value={})
@patch("api.bookshelf.get_read_books")
def test_get_last_read_book_missing_fields(mock_get_books, mock_read_book, client):
    fake_oid = ObjectId()
    mock_get_books.return_value = [
        {
            "book_id": "507f1f77bcf86cd799439012",
            "date_finished": "2025-04-22",
            "_id": fake_oid,
        }
    ]
    res = client.get("/shelf/api/user/507f1f77bcf86cd799439011/books/lastread")
    assert res.status_code == 200
    assert "rating" in res.get_json()


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_read_books")
def test_get_read_books_success(mock_get_books, mock_read_book, client):
    uid = "507f1f77bcf86cd799439011"
    book_id = "507f1f77bcf86cd799439012"

    mock_get_books.return_value = [{"book_id": book_id, "rating": "pos"}]
    mock_read_book.return_value = {"title": "Read Book", "book_id": book_id}

    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert data[0]["rating"] == "pos"
    assert data[0]["title"] == "Read Book"


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_read_books")
def test_get_read_books_skips_bad_books(mock_get_books, mock_read_book, client):
    uid = "507f1f77bcf86cd799439011"
    book_id = "507f1f77bcf86cd799439012"

    mock_get_books.return_value = [{"book_id": book_id, "rating": "pos"}]
    mock_read_book.return_value = "Book not found"  # triggers skip

    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 200
    assert res.get_json() == []


@patch("api.bookshelf.get_read_books", return_value="Error: user not found")
def test_get_read_books_returns_error_string(mock_get_books, client):
    uid = "507f1f77bcf86cd799439011"
    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 400
    assert res.get_json()["error"] == "Error: user not found"


@patch("api.bookshelf.get_read_books", side_effect=Exception("Unexpected failure"))
def test_get_read_books_exception(mock_get_books, client):
    uid = "507f1f77bcf86cd799439011"
    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 500
    assert "Unexpected failure" in res.get_json()["error"]


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_read_books")
def test_get_read_books_partial_skip(mock_get_books, mock_read_book, client):
    uid = "507f1f77bcf86cd799439011"
    valid_id = "507f1f77bcf86cd799439012"
    invalid_id = "507f1f77bcf86cd799439013"

    mock_get_books.return_value = [
        {"book_id": valid_id, "rating": "pos"},
        {"book_id": invalid_id, "rating": "mid"},
    ]

    def read_book_side_effect(book_id):
        if book_id == valid_id:
            return {"title": "Valid Book", "book_id": valid_id}
        else:
            return "Error retrieving book"

    mock_read_book.side_effect = read_book_side_effect

    res = client.get(f"/shelf/api/user/{uid}/books/read")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["book_id"] == valid_id


@patch("api.bookshelf.get_unread_books", return_value="Error: no user found")
def test_get_unread_books_returns_error_string(mock_get_books, client):
    uid = "507f1f77bcf86cd799439011"

    res = client.get(f"/shelf/api/user/{uid}/books/to-read")
    assert res.status_code == 400
    assert res.get_json()["error"] == "Error: no user found"


@patch("api.bookshelf.get_unread_books", side_effect=Exception("DB exploded"))
def test_get_unread_books_raises_exception(mock_get_books, client):
    uid = "507f1f77bcf86cd799439011"

    res = client.get(f"/shelf/api/user/{uid}/books/to-read")
    assert res.status_code == 500
    assert "DB exploded" in res.get_json()["error"]


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_unread_books")
def test_get_unread_books_with_objectid_conversion(
    mock_get_books, mock_read_book, client
):
    uid = "507f1f77bcf86cd799439011"
    oid = ObjectId()
    mock_get_books.return_value = [{"book_id": "507f1f77bcf86cd799439012"}]
    mock_read_book.return_value = {"_id": oid, "title": "ObjectId Book"}

    res = client.get(f"/shelf/api/user/{uid}/books/to-read")
    assert res.status_code == 200
    result = res.get_json()
    assert result[0]["_id"] == str(oid)


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_currently_reading_books")
def test_get_currently_reading_book_success(mock_get_books, mock_read_book, client):
    uid = "507f1f77bcf86cd799439011"
    bid = "507f1f77bcf86cd799439012"

    mock_get_books.return_value = [{"book_id": bid}]
    mock_read_book.return_value = {"book_id": bid, "title": "Reading Book"}

    res = client.get(f"/shelf/api/user/{uid}/books/currently-reading")
    assert res.status_code == 200
    data = res.get_json()
    assert data["title"] == "Reading Book"


@patch("api.bookshelf.get_currently_reading_books", return_value=[])
def test_get_currently_reading_book_empty(mock_get_books, client):
    uid = "507f1f77bcf86cd799439011"

    res = client.get(f"/shelf/api/user/{uid}/books/currently-reading")
    assert res.status_code == 400
    assert "No books currently reading" in res.get_json()["error"]


@patch(
    "api.bookshelf.get_currently_reading_books", side_effect=Exception("Database down")
)
def test_get_currently_reading_book_crashes(mock_get_books, client):
    uid = "507f1f77bcf86cd799439011"

    res = client.get(f"/shelf/api/user/{uid}/books/currently-reading")
    assert res.status_code == 500
    assert "Database down" in res.get_json()["error"]


@patch("api.bookshelf.read_book_by_bookId")
@patch("api.bookshelf.get_currently_reading_books")
def test_get_currently_reading_book_objectid_conversion(
    mock_get_books, mock_read_book, client
):
    uid = "507f1f77bcf86cd799439011"
    bid = "507f1f77bcf86cd799439012"
    oid = ObjectId()

    mock_get_books.return_value = [{"book_id": bid}]
    mock_read_book.return_value = {"_id": oid, "title": "Reading Book"}

    res = client.get(f"/shelf/api/user/{uid}/books/currently-reading")
    assert res.status_code == 200
    assert res.get_json()["_id"] == str(oid)


@patch("api.bookshelf.create_user_bookshelf", return_value="mock_id")
@patch("api.bookshelf.get_currently_reading_books", return_value=[])
def test_add_book_to_bookshelf_success(mock_get, mock_create, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.post(
        f"/shelf/api/user/{uid}/bookshelf",
        json={"book_id": bid, "status": "read", "rating": "pos"},
    )

    assert res.status_code == 201
    assert res.get_json()["message"] == "Book added to bookshelf"
    assert res.get_json()["id"] == "mock_id"


@patch("api.bookshelf.create_user_bookshelf", return_value="Error: already exists")
@patch("api.bookshelf.get_currently_reading_books", return_value=[])
def test_add_book_to_bookshelf_creation_error(mock_get, mock_create, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.post(
        f"/shelf/api/user/{uid}/bookshelf",
        json={"book_id": bid, "status": "read", "rating": "pos"},
    )

    assert res.status_code == 400
    assert "already exists" in res.get_json()["error"]


@patch("api.bookshelf.create_user_bookshelf", return_value="mock_id")
@patch("api.bookshelf.delete_user_bookshelf")
@patch("api.bookshelf.get_currently_reading_books")
def test_add_currently_reading_replaces_existing(
    mock_get, mock_delete, mock_create, client
):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())
    old_bid = str(ObjectId())

    mock_get.return_value = [{"book_id": old_bid}]
    mock_delete.return_value = "Deleted old entry"

    res = client.post(
        f"/shelf/api/user/{uid}/bookshelf",
        json={"book_id": bid, "status": "currently-reading", "rating": "mid"},
    )

    assert res.status_code == 201
    assert res.get_json()["message"] == "Book added to bookshelf"
    mock_delete.assert_called_once_with(uid, old_bid)


def test_add_book_to_bookshelf_missing_fields(client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.post(
        f"/shelf/api/user/{uid}/bookshelf",
        json={"book_id": bid},  # missing 'status' and 'rating'
    )

    assert res.status_code == 500
    assert "error" in res.get_json()


@patch("api.bookshelf.create_user_bookshelf", side_effect=Exception("Boom"))
@patch("api.bookshelf.get_currently_reading_books", return_value=[])
def test_add_book_to_bookshelf_crashes(mock_get, mock_create, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.post(
        f"/shelf/api/user/{uid}/bookshelf",
        json={"book_id": bid, "status": "read", "rating": "pos"},
    )

    assert res.status_code == 500
    assert "Boom" in res.get_json()["error"]


@patch(
    "api.bookshelf.update_page_number",
    return_value="UserBookshelf page number updated successfully.",
)
def test_update_current_page_success(mock_update, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
        json={"page_number": 42},
    )

    assert res.status_code == 200
    assert "updated successfully" in res.get_json()["message"]
    mock_update.assert_called_once_with(uid, bid, 42)


def test_update_current_page_invalid_negative(client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
        json={"page_number": -5},
    )

    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid page number"


def test_update_current_page_invalid_nonint(client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
        json={"page_number": "forty"},
    )

    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid page number"


@patch(
    "api.bookshelf.update_page_number", return_value="UserBookshelf entry not found."
)
def test_update_current_page_model_error(mock_update, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
        json={"page_number": 10},
    )

    assert res.status_code == 400
    assert res.get_json()["error"] == "UserBookshelf entry not found."


@patch("api.bookshelf.update_page_number", side_effect=Exception("Page update crash"))
def test_update_current_page_exception(mock_update, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
        json={"page_number": 99},
    )

    assert res.status_code == 500
    assert "Page update crash" in res.get_json()["error"]


@patch("api.bookshelf.get_page_number", return_value=42)
def test_get_current_page_success(mock_get, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page")

    assert res.status_code == 200
    assert res.get_json() == {"page_number": 42}
    mock_get.assert_called_once_with(uid, bid)


@patch("api.bookshelf.get_page_number", return_value="UserBookshelf entry not found")
def test_get_current_page_not_found(mock_get, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page")

    assert res.status_code == 404
    assert res.get_json()["error"] == "UserBookshelf entry not found"


@patch("api.bookshelf.get_page_number", side_effect=Exception("Get crash"))
def test_get_current_page_exception(mock_get, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page")

    assert res.status_code == 500
    assert "Get crash" in res.get_json()["error"]


@patch(
    "api.bookshelf.update_user_bookshelf_status",
    return_value="UserBookshelf status updated successfully.",
)
def test_update_bookshelf_status_success(mock_update, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/status",
        json={"status": "to-read"},
    )

    assert res.status_code == 200
    assert "Book status updated" in res.get_json()["message"]
    mock_update.assert_called_once_with(uid, bid, "to-read", date_finished=None)


@patch(
    "api.bookshelf.update_user_bookshelf_status",
    return_value="Error: Invalid status value.",
)
def test_update_bookshelf_status_model_error(mock_update, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/status",
        json={"status": "banana"},
    )

    assert res.status_code == 400
    assert "Invalid status" in res.get_json()["error"]


@patch(
    "api.bookshelf.update_user_bookshelf_status", side_effect=Exception("Status crash")
)
def test_update_bookshelf_status_crash(mock_update, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/status",
        json={"status": "read"},
    )

    assert res.status_code == 500
    assert "Status crash" in res.get_json()["error"]


@patch(
    "api.bookshelf.rate_book", return_value="UserBookshelf rating updated successfully."
)
def test_rate_book_success(mock_rate, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/rating",
        json={"rating": "pos"},
    )

    assert res.status_code == 200
    assert res.get_json()["message"] == "Book rating updated."
    mock_rate.assert_called_once_with(uid, bid, "pos")


@patch("api.bookshelf.rate_book", return_value="Error: Invalid rating value.")
def test_rate_book_invalid_rating(mock_rate, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/rating",
        json={"rating": "amazing"},
    )

    assert res.status_code == 400
    assert "Invalid rating" in res.get_json()["error"]


@patch("api.bookshelf.rate_book", side_effect=Exception("Rating logic failed"))
def test_rate_book_exception(mock_rate, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.put(
        f"/shelf/api/user/{uid}/bookshelf/{bid}/rating",
        json={"rating": "mid"},
    )

    assert res.status_code == 500
    assert "Rating logic failed" in res.get_json()["error"]


@patch(
    "api.bookshelf.delete_user_bookshelf",
    return_value="UserBookshelf entry deleted successfully.",
)
def test_delete_book_from_bookshelf_success(mock_delete, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
    assert res.status_code == 200
    assert "deleted" in res.get_json()["message"]
    mock_delete.assert_called_once_with(uid, bid)


@patch("api.bookshelf.delete_user_bookshelf", return_value="Error: Invalid user_id.")
def test_delete_book_from_bookshelf_model_error(mock_delete, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
    assert res.status_code == 400
    assert "Invalid user_id" in res.get_json()["error"]
    mock_delete.assert_called_once_with(uid, bid)


@patch("api.bookshelf.delete_user_bookshelf", side_effect=Exception("Delete exploded"))
def test_delete_book_from_bookshelf_exception(mock_delete, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
    assert res.status_code == 500
    assert "Delete exploded" in res.get_json()["error"]


@patch("api.bookshelf.get_bookshelf_status", return_value="read")
def test_get_book_status_success(mock_get_status, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/status")
    assert res.status_code == 200
    assert res.get_json()["status"] == "read"
    mock_get_status.assert_called_once_with(uid, bid)


@patch("api.bookshelf.get_bookshelf_status", return_value="Error: Invalid book_id.")
def test_get_book_status_model_error(mock_get_status, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/status")
    assert res.status_code == 400
    assert "Invalid book_id" in res.get_json()["error"]
    mock_get_status.assert_called_once_with(uid, bid)


@patch(
    "api.bookshelf.get_bookshelf_status", side_effect=Exception("Status fetch error")
)
def test_get_book_status_exception(mock_get_status, client):
    uid = "507f1f77bcf86cd799439011"
    bid = str(ObjectId())

    res = client.get(f"/shelf/api/user/{uid}/bookshelf/{bid}/status")
    assert res.status_code == 500
    assert "Status fetch error" in res.get_json()["error"]
