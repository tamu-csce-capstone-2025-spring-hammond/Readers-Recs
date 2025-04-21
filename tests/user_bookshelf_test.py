import pytest
import uuid
from datetime import datetime, date
from bson import ObjectId
from bson.errors import InvalidId
from backend.models.user_bookshelf import (
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
from backend.models.users import create_user, delete_user
from backend.models.books import create_book, delete_book
import pytz


@pytest.fixture
def user_and_book():
    u = uuid.uuid4().hex
    uid = create_user(
        first_name="UBTest",
        last_name="User",
        username=f"ubuser_{u}",
        email_address=f"ub_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={"age": 30},
    )
    bid = create_book(
        title="UBook",
        author=["Author"],
        page_count=100,
        genre="Test",
        tags=["ub"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["test"],
    )
    yield uid, bid
    delete_user_bookshelf(uid, bid)
    delete_user(uid)
    delete_book(bid)


def test_update_user_bookshelf_status_edge_cases(user_and_book):
    uid, bid = user_and_book
    # malformed ids should return generic errors
    assert update_user_bookshelf_status("bad", bid, "read").startswith("Error:")
    assert update_user_bookshelf_status(uid, "bad", "read").startswith("Error:")
    # well-formed but nonexistent book id, invalid book_id
    fake = str(ObjectId())
    assert (
        update_user_bookshelf_status(uid, fake, "read")
        == "UserBookshelf entry not found."
    )


def test_rate_book_errors_and_success(user_and_book):
    uid, bid = user_and_book
    assert rate_book("bad", bid, "pos").startswith("Error:")
    assert rate_book(uid, "bad", "pos") == "Error: Invalid user_id or book_id."
    fake = str(ObjectId())
    assert rate_book(uid, fake, "pos") == "Error: Invalid book_id."

    create_user_bookshelf(uid, bid, status="read")
    # Confirm the book is considered read before testing invalid rating
    assert get_bookshelf_status(uid, bid) == "read"

    # Now this will trigger the invalid rating branch
    assert rate_book(uid, bid, "excellent") == "Error: Invalid rating value."
    assert rate_book(uid, bid, "pos") == "UserBookshelf rating updated successfully."
    assert rate_book(uid, bid, "neg") == "UserBookshelf rating updated successfully."


def test_delete_user_bookshelf_errors(user_and_book):
    uid, bid = user_and_book
    # invalid user_id
    assert delete_user_bookshelf("bad", bid) == "Error: Invalid user_id or book_id."
    # invalid book_id
    assert delete_user_bookshelf(uid, "bad") == "Error: Invalid user_id or book_id."
    # well-formed but no entry
    fake_bid = str(ObjectId())
    assert delete_user_bookshelf(uid, fake_bid) == "Error: Invalid book_id."


def test_retrieve_user_bookshelf_invalid_and_valid(user_and_book):
    uid, bid = user_and_book
    # invalid user_id yields empty list
    assert retrieve_user_bookshelf("bad") == []

    # valid user but no "read" entries
    assert retrieve_user_bookshelf(uid) == []
    # add a "read" entry and verify retrieval
    sid = create_user_bookshelf(uid, bid, status="read")
    books = retrieve_user_bookshelf(uid)
    assert isinstance(books, list) and all(
        item.get("status") == "read" for item in books
    )
    delete_user_bookshelf(uid, bid)


def test_get_bookshelf_status_various_states(user_and_book):
    uid, bid = user_and_book
    # no entry -> no-status
    assert get_bookshelf_status(uid, bid) == "no-status"
    # malformed book_id -> error
    assert get_bookshelf_status(uid, "bad") == "Error: Invalid book_id."
    # to-read state
    sid = create_user_bookshelf(uid, bid, status="to-read")
    assert get_bookshelf_status(uid, bid) == "to-read"
    delete_user_bookshelf(uid, bid)
    # currently-reading state
    sid = create_user_bookshelf(uid, bid, status="currently-reading")
    assert get_bookshelf_status(uid, bid) == "currently-reading"
    delete_user_bookshelf(uid, bid)
    # read state
    sid = create_user_bookshelf(uid, bid, status="read")
    assert get_bookshelf_status(uid, bid) == "read"
    delete_user_bookshelf(uid, bid)


def test_get_read_books_empty_and_invalid(user_and_book):
    uid, bid = user_and_book
    # invalid user
    assert get_read_books("bad") == "Error: Invalid user_id."
    # no entries
    assert get_read_books(uid) == []
    # with a read entry
    sid = create_user_bookshelf(uid, bid, status="read")
    reads = get_read_books(uid)
    assert (
        isinstance(reads, list) and len(reads) == 1 and reads[0].get("status") == "read"
    )
    delete_user_bookshelf(uid, bid)


def test_get_unread_books_empty_and_valid(user_and_book):
    uid, bid = user_and_book
    # no entries
    assert get_unread_books(uid) == []
    # with an unread entry (to-read)
    sid = create_user_bookshelf(uid, bid, status="to-read")
    unread = get_unread_books(uid)
    assert (
        isinstance(unread, list)
        and len(unread) == 1
        and unread[0].get("status") == "to-read"
    )
    delete_user_bookshelf(uid, bid)


def test_get_currently_reading_books_empty_and_invalid(user_and_book):
    uid, bid = user_and_book
    # invalid user
    assert get_currently_reading_books("bad") == "Error: Invalid user_id."
    # no entries -> None
    assert get_currently_reading_books(uid) is None
    # with an entry
    sid = create_user_bookshelf(uid, bid, status="currently-reading")
    curr = get_currently_reading_books(uid)
    assert isinstance(curr, list) and curr[0].get("status") == "currently-reading"
    delete_user_bookshelf(uid, bid)


def test_rate_book_before_and_after_read_and_invalid_rating(user_and_book):
    uid, bid = user_and_book
    # before any shelf entry (no read entry yet)
    assert rate_book(uid, bid, "pos") == "Error: Book has not been read yet."
    # malformed ids
    assert rate_book("bad", bid, "pos").startswith("Error:")
    assert rate_book(uid, "bad", "pos") == "Error: Invalid user_id or book_id."

    # valid read but invalid rating
    create_user_bookshelf(uid, bid, status="read")
    assert rate_book(uid, bid, "wrong") == "Error: Invalid rating value."

    # valid ratings
    assert rate_book(uid, bid, "pos") == "UserBookshelf rating updated successfully."
    entry = retrieve_user_bookshelf(uid)[0]
    assert entry.get("rating") == "pos"
    assert rate_book(uid, bid, "neg") == "UserBookshelf rating updated successfully."
    entry2 = retrieve_user_bookshelf(uid)[0]
    assert entry2.get("rating") == "neg"


def test_create_user_bookshelf_invalid_inputs():
    fake = str(ObjectId())
    assert create_user_bookshelf("bad", fake) == "Error: Invalid user_id or book_id."
    assert create_user_bookshelf(fake, "bad") == "Error: Invalid user_id."


def test_update_user_bookshelf_status_invalid_status(user_and_book):
    uid, bid = user_and_book
    create_user_bookshelf(uid, bid)
    result = update_user_bookshelf_status(uid, bid, "invalid")
    assert result == "Error: Invalid status value."


def test_get_unread_books_invalid_user():
    assert get_unread_books("bad") == []


def test_update_page_number_errors(user_and_book):
    uid, bid = user_and_book
    assert update_page_number("bad", bid, 10) == "Error: Invalid user_id or book_id."
    assert update_page_number(uid, "bad", 10) == "Error: Invalid user_id or book_id."
    assert (
        update_page_number(uid, bid, -5)
        == "Error: Invalid page number. It must be a non-negative integer."
    )
    assert update_page_number(uid, bid, 10) == "UserBookshelf entry not found."


def test_get_page_number_errors(user_and_book):
    uid, bid = user_and_book
    assert get_page_number("bad", bid) == "Error: Invalid user_id or book_id."
    assert get_page_number(uid, "bad") == "Error: Invalid user_id or book_id."
    assert get_page_number(uid, bid) == "UserBookshelf entry not found."


def test_get_page_number_valid(user_and_book):
    uid, bid = user_and_book
    create_user_bookshelf(uid, bid, status="currently-reading")
    update_page_number(uid, bid, 42)
    page = get_page_number(uid, bid)
    assert page == 42


def test_create_user_bookshelf_duplicate(user_and_book):
    uid, bid = user_and_book
    first = create_user_bookshelf(uid, bid, status="to-read")
    assert isinstance(first, str)
    second = create_user_bookshelf(uid, bid, status="to-read")
    assert second == "Error: book already present in user bookshelf."
    delete_user_bookshelf(uid, bid)


def test_create_user_bookshelf_schema_validation_error(user_and_book):
    uid, bid = user_and_book
    # Invalid status (not one of the expected pattern)
    result = create_user_bookshelf(uid, bid, status="invalid-status")
    assert result.startswith("Schema Validation Error:")


def test_get_bookshelf_status_invalid_id_type():
    result = get_bookshelf_status("fake_user", "not_an_oid")
    assert result.startswith("Error:")


def test_get_unread_books_force_exception(monkeypatch):
    def raise_error(user_id):
        raise Exception("forced failure")

    from backend.models import user_bookshelf

    monkeypatch.setattr(user_bookshelf.user_bookshelf_collection, "find", raise_error)
    result = get_unread_books("some_user")
    assert result.startswith("Error: forced failure")


def test_rate_book_no_read_entry(user_and_book):
    uid, bid = user_and_book
    create_user_bookshelf(uid, bid, status="to-read")
    assert rate_book(uid, bid, "pos") == "Error: Book has not been read yet."


def test_update_page_number_float(user_and_book):
    uid, bid = user_and_book
    create_user_bookshelf(uid, bid, status="currently-reading")
    assert (
        update_page_number(uid, bid, 12.5)
        == "Error: Invalid page number. It must be a non-negative integer."
    )


def test_get_currently_reading_books_returns_none(user_and_book):
    uid, _ = user_and_book
    assert get_currently_reading_books(uid) is None


def test_update_user_bookshelf_status_success(user_and_book):
    uid, bid = user_and_book

    # Create the bookshelf entry with initial status
    sid = create_user_bookshelf(uid, bid, status="to-read")
    assert isinstance(sid, str)
    assert get_bookshelf_status(uid, bid) == "to-read"

    # Update the status to "read"
    result = update_user_bookshelf_status(uid, bid, "read")
    assert result == "UserBookshelf status updated successfully."

    # Confirm the update via model function
    assert get_bookshelf_status(uid, bid) == "read"


def test_create_user_bookshelf_with_date_objects(user_and_book):
    uid, bid = user_and_book
    d = date(2024, 1, 1)

    sid = create_user_bookshelf(
        uid, bid, status="read", date_started=d, date_finished=d
    )
    assert isinstance(sid, str)

    result = retrieve_user_bookshelf(uid)
    assert len(result) == 1
    assert result[0]["status"] == "read"
    assert result[0]["date_started"].isoformat().startswith("2024-01-01")
    assert result[0]["date_finished"].isoformat().startswith("2024-01-01")


def test_create_user_bookshelf_with_datetime_objects(user_and_book):
    uid, bid = user_and_book
    dt = datetime(2023, 5, 15, 12, 30)

    sid = create_user_bookshelf(
        uid, bid, status="read", date_started=dt, date_finished=dt
    )
    assert isinstance(sid, str)

    result = retrieve_user_bookshelf(uid)
    assert len(result) == 1
    assert result[0]["date_started"].isoformat().startswith("2023-05-15")
    assert result[0]["date_finished"].isoformat().startswith("2023-05-15")


def test_create_user_bookshelf_default_date_added(user_and_book):
    uid, bid = user_and_book

    sid = create_user_bookshelf(uid, bid, status="read")
    assert isinstance(sid, str)

    today_str = date.today().isoformat()
    result = retrieve_user_bookshelf(uid)
    assert len(result) == 1
    assert result[0]["date_added"].isoformat().startswith(today_str)


def test_get_bookshelf_status_generic_error(monkeypatch, user_and_book):
    uid, bid = user_and_book

    def fail_find(*_):
        raise Exception("Broken find")

    monkeypatch.setattr(
        "backend.models.user_bookshelf.user_bookshelf_collection.find_one",
        fail_find,
    )
    result = get_bookshelf_status(uid, bid)
    assert result.startswith("Error: Broken find")


def test_get_unread_books_generic_error(monkeypatch):
    def fail_find(*_):
        raise Exception("Unread error")

    monkeypatch.setattr(
        "backend.models.user_bookshelf.user_bookshelf_collection.find",
        fail_find,
    )
    result = get_unread_books("user")
    assert result.startswith("Error: Unread error")


def test_get_currently_reading_books_generic_error(monkeypatch):
    valid_user_id = str(ObjectId())

    def fail_find(*_):
        raise Exception("CR error")

    monkeypatch.setattr(
        "backend.models.user_bookshelf.user_bookshelf_collection.find",
        fail_find,
    )
    result = get_currently_reading_books(valid_user_id)
    assert result.startswith("Error: CR error")


def test_rate_book_generic_error(monkeypatch, user_and_book):
    uid, bid = user_and_book
    create_user_bookshelf(uid, bid, status="read")

    def fail_update(*_):
        raise Exception("Rate exploded")

    monkeypatch.setattr(
        "backend.models.user_bookshelf.user_bookshelf_collection.update_one",
        fail_update,
    )
    result = rate_book(uid, bid, "pos")
    assert result.startswith("Error: Rate exploded")
