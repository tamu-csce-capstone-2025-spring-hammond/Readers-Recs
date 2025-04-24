from unittest.mock import patch
import pytest
from bson.errors import InvalidId
from bson import ObjectId
from datetime import date
from models.user_bookshelf import (
    create_user_bookshelf,
    update_user_bookshelf_status,
    retrieve_user_bookshelf,
    get_bookshelf_status,
    get_read_books,
    get_unread_books,
    get_currently_reading_books,
    rate_book,
    update_page_number,
    get_page_number,
    delete_user_bookshelf,
)

# Mocked IDs used in all tests
uid = str(ObjectId())
bid = str(ObjectId())
fake_bid = str(ObjectId())
VALID_USER_ID = "68094b3267aa3dbf50919a51"
VALID_BOOK_ID = "68094b3267aa3dbf50919a52"

valid_ids = {
    "Users": {uid},
    "Books": {bid, fake_bid},
    "User_Bookshelf": {uid},  # optional
}


def validate_mock(collection, oid):
    if oid == "bad":
        return False
    return oid in valid_ids.get(collection, set())


@pytest.fixture
def user_and_book():
    return uid, bid


@patch("backend.models.user_bookshelf.user_bookshelf_collection")
@patch("backend.models.user_bookshelf.is_valid_object_id", side_effect=validate_mock)
def test_retrieve_user_bookshelf_valid(mock_valid, mock_collection, user_and_book):
    uid, _ = user_and_book
    mock_collection.find.return_value = [{"status": "read"}]
    books = retrieve_user_bookshelf(uid)
    assert isinstance(books, list)
    assert all(book["status"] == "read" for book in books)


@patch("models.user_bookshelf.ObjectId", side_effect=lambda x: x)
@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_bookshelf_status_valid(mock_valid, mock_collection, mock_oid):
    mock_valid.side_effect = lambda col, oid: True
    mock_collection.find_one.return_value = {"status": "read"}

    result = get_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "read"


@patch("models.user_bookshelf.ObjectId", side_effect=lambda x: x)
@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_bookshelf_status_no_status(mock_valid, mock_collection, mock_oid):
    mock_valid.side_effect = lambda col, oid: True
    mock_collection.find_one.return_value = None

    result = get_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "no-status"


@patch("models.user_bookshelf.ObjectId", side_effect=lambda x: x)
@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_bookshelf_status_invalid_id(mock_valid, mock_collection, mock_oid):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = get_bookshelf_status(VALID_USER_ID, "invalid_object_id")
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.ObjectId", side_effect=lambda x: x)
@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_bookshelf_status_exception(mock_valid, mock_collection, mock_oid):
    mock_valid.side_effect = lambda col, oid: True
    mock_collection.find_one.side_effect = Exception("Simulated failure")

    result = get_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID)
    assert result.startswith("Error: Simulated failure")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_unread_books_valid(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.return_value = [{"status": "to-read"}, {"status": "to-read"}]

    result = get_unread_books(uid)
    assert isinstance(result, list)
    assert all(book["status"] == "to-read" for book in result)


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_unread_books_empty(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.return_value = []

    result = get_unread_books(uid)
    assert result == []


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_unread_books_invalid_user(mock_valid, mock_collection):
    mock_valid.return_value = False

    result = get_unread_books("bad")
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_currently_reading_books_valid(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.return_value = [{"status": "currently-reading"}]

    result = get_currently_reading_books(uid)
    assert isinstance(result, list)
    assert result[0]["status"] == "currently-reading"


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_currently_reading_books_none(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.return_value = []

    result = get_currently_reading_books(uid)
    assert result is None


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_currently_reading_books_invalid_user(mock_valid, mock_collection):
    mock_valid.return_value = False

    result = get_currently_reading_books("bad")
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_unread_books_exception(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.side_effect = Exception("Simulated unread error")

    result = get_unread_books(uid)
    assert result.startswith("Error: Simulated unread error")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_currently_reading_books_exception(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.side_effect = Exception("Simulated currently-reading error")

    result = get_currently_reading_books(uid)
    assert result.startswith("Error: Simulated currently-reading error")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_read_books_valid(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.return_value = [{"status": "read"}, {"status": "read"}]

    result = get_read_books(uid)
    assert isinstance(result, list)
    assert all(book["status"] == "read" for book in result)


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_read_books_empty(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.return_value = []

    result = get_read_books(uid)
    assert result == []


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_read_books_invalid_user(mock_valid, mock_collection):
    mock_valid.return_value = False

    result = get_read_books("bad")
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_read_books_exception(mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"

    mock_valid.return_value = True
    mock_collection.find.side_effect = Exception("Simulated read error")

    result = get_read_books(uid)
    assert result.startswith("Error: Simulated read error")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_rate_book_success(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.count_documents.return_value = 1
    mock_collection.update_one.return_value.matched_count = 1

    result = rate_book(VALID_USER_ID, VALID_BOOK_ID, "pos")
    assert result == "UserBookshelf rating updated successfully."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_rate_book_invalid_user(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Users" else True

    result = rate_book("bad_user", VALID_BOOK_ID, "pos")
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_rate_book_invalid_book(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = rate_book(VALID_USER_ID, "bad_book", "pos")
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_rate_book_not_read(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.count_documents.return_value = 0

    result = rate_book(VALID_USER_ID, VALID_BOOK_ID, "pos")
    assert result == "Error: Book has not been read yet."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_rate_book_invalid_rating(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.count_documents.return_value = 1

    result = rate_book(VALID_USER_ID, VALID_BOOK_ID, "excellent")
    assert result == "Error: Invalid rating value."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_rate_book_update_exception(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.count_documents.return_value = 1
    mock_collection.update_one.side_effect = Exception(
        "Simulated rating update failure"
    )

    result = rate_book(VALID_USER_ID, VALID_BOOK_ID, "pos")
    assert result.startswith("Error: Simulated rating update failure")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_success(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.update_one.return_value.matched_count = 1

    result = update_page_number(VALID_USER_ID, VALID_BOOK_ID, 42)
    assert result == "Page number updated successfully."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_invalid_user(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Users" else True

    result = update_page_number("bad_user", VALID_BOOK_ID, 10)
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_invalid_book(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = update_page_number(VALID_USER_ID, "bad_book", 10)
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_negative(mock_valid, mock_collection):
    mock_valid.return_value = True

    result = update_page_number(VALID_USER_ID, VALID_BOOK_ID, -5)
    assert result == "Error: Invalid page number. It must be a non-negative integer."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_non_integer(mock_valid, mock_collection):
    mock_valid.return_value = True

    result = update_page_number(VALID_USER_ID, VALID_BOOK_ID, "forty-two")
    assert result == "Error: Invalid page number. It must be a non-negative integer."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_not_found(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.update_one.return_value.matched_count = 0

    result = update_page_number(VALID_USER_ID, VALID_BOOK_ID, 10)
    assert result == "UserBookshelf entry not found."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_page_number_exception(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.update_one.side_effect = Exception("Simulated update error")

    result = update_page_number(VALID_USER_ID, VALID_BOOK_ID, 15)
    assert result.startswith("Error: Simulated update error")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
@patch("models.user_bookshelf.ObjectId", side_effect=InvalidId("bad ObjectId"))
def test_update_page_number_invalid_objectid(mock_oid, mock_valid, mock_collection):
    uid = "68094b3267aa3dbf50919a51"
    bid = "68094b3267aa3dbf50919a52"

    mock_valid.return_value = True

    result = update_page_number(uid, bid, 20)
    assert result == "Error: Invalid user_id or book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_page_number_valid(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = {"page_number": 42}

    result = get_page_number(VALID_USER_ID, VALID_BOOK_ID)
    assert result == 42


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_page_number_invalid_user(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Users" else True

    result = get_page_number("bad_user", VALID_BOOK_ID)
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_page_number_invalid_book(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = get_page_number(VALID_USER_ID, "bad_book")
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_page_number_entry_not_found(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = None

    result = get_page_number(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "UserBookshelf entry not found."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_get_page_number_generic_exception(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.side_effect = Exception("Simulated find error")

    result = get_page_number(VALID_USER_ID, VALID_BOOK_ID)
    assert result.startswith("Error: Simulated find error")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
@patch("models.user_bookshelf.ObjectId", side_effect=InvalidId("invalid ObjectId"))
def test_get_page_number_invalid_objectid(mock_oid, mock_valid, mock_collection):
    mock_valid.return_value = True

    result = get_page_number(VALID_USER_ID, VALID_BOOK_ID)
    assert result.startswith("Error: Invalid user_id or book_id.")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_success(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = "mock_id"

    result = create_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID, status="read")
    assert result == "mock_id"


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_duplicate(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = {"status": "read"}

    result = create_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID, status="read")
    assert result == "Error: book already present in user bookshelf."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_invalid_user(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Users" else True

    result = create_user_bookshelf("bad_user", VALID_BOOK_ID)
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_invalid_book(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = create_user_bookshelf(VALID_USER_ID, "bad_book")
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_validation_error(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = None

    result = create_user_bookshelf(
        VALID_USER_ID, VALID_BOOK_ID, status="invalid-status"
    )
    assert result.startswith("Schema Validation Error:")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
@patch("models.user_bookshelf.ObjectId", side_effect=InvalidId("bad id"))
def test_create_user_bookshelf_invalid_objectid(mock_oid, mock_valid, mock_collection):
    mock_valid.return_value = True

    result = create_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "Error: Invalid user_id or book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_generic_exception(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.side_effect = Exception("insert failed")

    result = create_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID)
    assert result.startswith("Error: insert failed")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_delete_user_bookshelf_success(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.delete_one.return_value.deleted_count = 1

    result = delete_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "UserBookshelf entry deleted successfully."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_delete_user_bookshelf_not_found(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.delete_one.return_value.deleted_count = 0

    result = delete_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "UserBookshelf entry not found."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_delete_user_bookshelf_invalid_user(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Users" else True

    result = delete_user_bookshelf("bad_user", VALID_BOOK_ID)
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_delete_user_bookshelf_invalid_book(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = delete_user_bookshelf(VALID_USER_ID, "bad_book")
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
@patch("models.user_bookshelf.ObjectId", side_effect=InvalidId("bad id"))
def test_delete_user_bookshelf_invalid_objectid(mock_oid, mock_valid, mock_collection):
    mock_valid.return_value = True

    result = delete_user_bookshelf(VALID_USER_ID, VALID_BOOK_ID)
    assert result == "Error: Invalid user_id or book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_user_bookshelf_status_success(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.update_one.return_value.matched_count = 1

    result = update_user_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID, "read")
    assert result == "UserBookshelf status updated successfully."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_user_bookshelf_status_invalid_user(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Users" else True

    result = update_user_bookshelf_status("bad_user", VALID_BOOK_ID, "read")
    assert result == "Error: Invalid user_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_user_bookshelf_status_invalid_book(mock_valid, mock_collection):
    mock_valid.side_effect = lambda col, oid: False if col == "Books" else True

    result = update_user_bookshelf_status(VALID_USER_ID, "bad_book", "read")
    assert result == "Error: Invalid book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_user_bookshelf_status_invalid_status_value(mock_valid, mock_collection):
    mock_valid.return_value = True

    result = update_user_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID, "shelved")
    assert result == "Error: Invalid status value."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_user_bookshelf_status_not_found(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.update_one.return_value.matched_count = 0

    result = update_user_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID, "read")
    assert result == "UserBookshelf entry not found."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_update_user_bookshelf_status_exception(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.update_one.side_effect = Exception("Simulated update failure")

    result = update_user_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID, "read")
    assert result.startswith("Error: Simulated update failure")


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
@patch("models.user_bookshelf.ObjectId", side_effect=InvalidId("invalid ObjectId"))
def test_update_user_bookshelf_status_invalid_objectid(
    mock_oid, mock_valid, mock_collection
):
    mock_valid.return_value = True

    result = update_user_bookshelf_status(VALID_USER_ID, VALID_BOOK_ID, "read")
    assert result == "Error: Invalid user_id or book_id."


@patch("models.user_bookshelf.user_bookshelf_collection")
@patch("models.user_bookshelf.is_valid_object_id")
def test_create_user_bookshelf_with_date_conversion(mock_valid, mock_collection):
    mock_valid.return_value = True
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = "mock_id"

    d = date(2024, 4, 1)

    result = create_user_bookshelf(
        VALID_USER_ID, VALID_BOOK_ID, status="read", date_started=d, date_finished=d
    )
    assert result == "mock_id"
