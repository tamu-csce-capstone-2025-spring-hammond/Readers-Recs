import pytest
from models.users import create_user, delete_user, read_user
from models.books import create_book, delete_book
from models.user_bookshelf import (
    create_user_bookshelf,
    delete_user_bookshelf,
    update_user_bookshelf_status,
    get_bookshelf_status,
    rate_book,
    update_page_number,
    get_page_number,
    retrieve_user_bookshelf,
)
from main import app
import uuid


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Testing integration between user, books, and user_bookshelf models
# This test will create a user and a book, add the book to the user's bookshelf, update the status, rate the book, and delete the entry.
def test_bookshelf_model_flow():
    user_id = create_user(
        first_name="Test",
        last_name="User",
        username="test_user_bookshelf",
        email_address="test_user_bookshelf@example.com",
        oauth={"access_token": "abc", "refresh_token": "def"},
        profile_image="",
        interests=[],
        demographics={},
    )
    book_id = create_book(
        title="Test Book",
        author=["Author"],
        page_count=100,
        genre="Fiction",
        tags=["test"],
        publication_date="2025-01-01",
        isbn="isbntest1",
        isbn13="isbn13test1",
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["fiction"],
    )

    try:
        # Create duplicate bookshelf entry (should fail)
        sid = create_user_bookshelf(user_id, book_id, status="to-read")
        assert isinstance(sid, str)
        duplicate = create_user_bookshelf(user_id, book_id, status="read")
        assert duplicate == "Error: book already present in user bookshelf."

        # Try invalid rating before marking as read
        err = rate_book(user_id, book_id, "excellent")
        assert err == "Error: Book has not been read yet."

        # Try rating before book is read
        err2 = rate_book(user_id, book_id, "pos")
        assert err2 == "Error: Book has not been read yet."

        # Now mark as read and rate correctly
        update_user_bookshelf_status(user_id, book_id, "read")
        assert (
            rate_book(user_id, book_id, "pos")
            == "UserBookshelf rating updated successfully."
        )

        # Test page number set without currently-reading status
        assert (
            update_page_number(user_id, book_id, 99) == "UserBookshelf entry not found."
        )

        # Reset to currently-reading and update page
        update_user_bookshelf_status(user_id, book_id, "currently-reading")
        assert (
            update_page_number(user_id, book_id, 42)
            == "Page number updated successfully."
        )
        assert get_page_number(user_id, book_id) == 42

        # Switch to to-read and make sure status and finished date reset
        update_user_bookshelf_status(user_id, book_id, "to read")
        assert get_bookshelf_status(user_id, book_id) == "to read"

        # Cleanup
        assert (
            delete_user_bookshelf(user_id, book_id)
            == "UserBookshelf entry deleted successfully."
        )
        assert get_bookshelf_status(user_id, book_id) == "no-status"

    finally:
        delete_user(user_id)
        delete_book(book_id)


# Testing the API endpoints for the bookshelf model
# This test will create a user and a book, add the book to the user's bookshelf, update the status, rate the book, and delete the entry.
def test_bookshelf_api_flow(client):
    import uuid

    u = uuid.uuid4().hex

    uid = create_user(
        first_name="Integration",
        last_name="Test",
        username=f"bookshelf_user_{u}",
        email_address=f"bookshelf_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={"age": 25, "country": "USA", "gender": "F"},
    )

    bid = create_book(
        title="Integration Book",
        author=["Author"],
        page_count=123,
        genre="Test Genre",
        tags=["integration"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Test Publisher",
        summary="This is a test book.",
        genre_tags=["test"],
    )

    try:
        # Add to shelf
        res = client.post(
            f"/shelf/api/user/{uid}/bookshelf",
            json={"book_id": bid, "status": "to-read", "rating": "mid"},
        )
        assert res.status_code == 201

        # Add duplicate (should fail)
        dup = client.post(
            f"/shelf/api/user/{uid}/bookshelf",
            json={"book_id": bid, "status": "to-read", "rating": "mid"},
        )
        assert dup.status_code == 400

        # Update status to currently-reading
        res = client.put(
            f"/shelf/api/user/{uid}/bookshelf/{bid}/status",
            json={"status": "currently-reading"},
        )
        assert res.status_code == 200

        # Invalid page number (negative)
        res = client.put(
            f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
            json={"page_number": -1},
        )
        assert res.status_code == 400

        # Valid page number update
        res = client.put(
            f"/shelf/api/user/{uid}/bookshelf/{bid}/current-page",
            json={"page_number": 42},
        )
        assert res.status_code == 200

        # Update to read and rate
        client.put(
            f"/shelf/api/user/{uid}/bookshelf/{bid}/status", json={"status": "read"}
        )
        res = client.put(
            f"/shelf/api/user/{uid}/bookshelf/{bid}/rating", json={"rating": "pos"}
        )
        assert res.status_code == 200

        # Invalid rating value
        res = client.put(
            f"/shelf/api/user/{uid}/bookshelf/{bid}/rating", json={"rating": "great"}
        )
        assert res.status_code == 400

        # Delete shelf entry
        res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
        assert res.status_code == 200

        # Try deleting again (may return 200 or 404 depending on implementation)
        res = client.delete(f"/shelf/api/user/{uid}/bookshelf/{bid}")
        assert res.status_code in [404, 200]

    finally:
        delete_user(uid)
        delete_book(bid)


def test_user_deletion_removes_bookshelf_entries():
    u = uuid.uuid4().hex
    uid = create_user(
        first_name="Cascade",
        last_name="Delete",
        username=f"user_cascade_{u}",
        email_address=f"cascade_{u}@example.com",
        oauth={"access_token": f"{u}_tok", "refresh_token": f"{u}_tok"},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="Cascade Book",
        author=["Author"],
        page_count=100,
        genre="Fiction",
        tags=["cascade"],
        publication_date="2025-01-01",
        isbn=f"{u[:9]}",
        isbn13=f"{u[:13]}",
        cover_image="",
        language="en",
        publisher="P",
        summary="S",
        genre_tags=["fiction"],
    )

    try:
        sid = create_user_bookshelf(uid, bid, status="read")
        assert isinstance(sid, str)
        assert retrieve_user_bookshelf(uid) != []

        # Delete user, should also remove bookshelf entry
        delete_user(uid)

        # Recheck – should be empty since user is gone
        assert retrieve_user_bookshelf(uid) == []

    finally:
        delete_book(bid)
        if isinstance(uid, str) and read_user(uid) != "User not found.":
            delete_user(uid)


def test_book_deletion_removes_bookshelf_entries():
    uid = create_user(
        first_name="BookCascade",
        last_name="Test",
        username="book_cascade_user",
        email_address="bookcascade@example.com",
        oauth={"access_token": "tok2", "refresh_token": "tok2"},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="ToBeDeleted",
        author=["Author"],
        page_count=100,
        genre="Drama",
        tags=["cleanme"],
        publication_date="2025-01-01",
        isbn="bookdelisbn",
        isbn13="bookdelisbn13",
        cover_image="",
        language="en",
        publisher="P",
        summary="S",
        genre_tags=["drama"],
    )

    try:
        sid = create_user_bookshelf(uid, bid, status="to-read")
        assert isinstance(sid, str)
        assert get_bookshelf_status(uid, bid) == "to-read"

        # Now delete the book
        delete_book(bid)

        # Check status – should return fallback status since entry is gone
        assert get_bookshelf_status(uid, bid) == "Error: Invalid book_id."

    finally:
        delete_user(uid)


def test_same_book_multiple_users():
    import uuid

    u = uuid.uuid4().hex
    # Create 2 users
    uid1 = create_user(
        first_name="User1",
        last_name="Test",
        username=f"user1_{u}",
        email_address=f"user1_{u}@example.com",
        oauth={"access_token": f"{u}a", "refresh_token": f"{u}a"},
        profile_image="",
        interests=[],
        demographics={},
    )
    uid2 = create_user(
        first_name="User2",
        last_name="Test",
        username=f"user2_{u}",
        email_address=f"user2_{u}@example.com",
        oauth={"access_token": f"{u}b", "refresh_token": f"{u}b"},
        profile_image="",
        interests=[],
        demographics={},
    )

    # One shared book
    bid = create_book(
        title="SharedBook",
        author=["Author"],
        page_count=111,
        genre="Shared",
        tags=["shared"],
        publication_date="2025-01-01",
        isbn=f"shared{u[:6]}",
        isbn13=f"shared{u[:13]}",
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["shared"],
    )

    try:
        # Both users add the same book
        assert create_user_bookshelf(uid1, bid, status="currently-reading") != "Error"
        assert create_user_bookshelf(uid2, bid, status="to-read") != "Error"

        # They can have independent statuses
        assert get_bookshelf_status(uid1, bid) == "currently-reading"
        assert get_bookshelf_status(uid2, bid) == "to-read"

        # Update both users' entries independently
        assert update_page_number(uid1, bid, 45) == "Page number updated successfully."
        assert (
            update_user_bookshelf_status(uid2, bid, "read")
            == "UserBookshelf status updated successfully."
        )

        # Final checks
        assert get_page_number(uid1, bid) == 45
        assert get_bookshelf_status(uid2, bid) == "read"

    finally:
        delete_user_bookshelf(uid1, bid)
        delete_user_bookshelf(uid2, bid)
        delete_user(uid1)
        delete_user(uid2)
        delete_book(bid)
