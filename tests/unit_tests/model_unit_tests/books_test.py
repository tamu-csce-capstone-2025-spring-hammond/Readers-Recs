import pytest
from unittest.mock import MagicMock
from bson import ObjectId
import models.books as book_model
from datetime import datetime


# Patch books_collection globally
@pytest.fixture(autouse=True)
def mock_books_collection(monkeypatch):
    fake_id = ObjectId()
    valid_doc = {
        "_id": fake_id,
        "title": "Mocked Book",
        "author": ["Author"],
        "page_count": 100,
        "genre": "Fiction",
        "tags": ["test"],
        "publication_date": datetime(2025, 1, 1),  # valid datetime
        "isbn": "mockisbn",
        "isbn13": "mockisbn13",
        "cover_image": "http://example.com/image.jpg",
        "language": "en",
        "publisher": "MockPub",
        "summary": "Mock summary",
        "genre_tags": ["fiction"],
        "embedding": [],
    }

    mock_col = MagicMock()
    mock_col.insert_one.return_value.inserted_id = fake_id
    mock_col.find_one.side_effect = lambda q, *args, **kwargs: (
        valid_doc
        if ("_id" in q and q["_id"] == fake_id)
        or ("isbn" in q and q["isbn"] == "mockisbn")
        or ("title" in q and q["title"] == "Mocked Book")
        or ("isbn13" in q and q["isbn13"] == "mockisbn13")
        else None
    )
    mock_col.update_one.return_value.modified_count = 1
    mock_col.delete_one.return_value.deleted_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)
    return str(fake_id)


def test_create_book_success(monkeypatch):
    fake_id = ObjectId()

    mock_col = MagicMock()
    mock_col.find_one.return_value = None  # Not a duplicate
    mock_col.insert_one.return_value.inserted_id = fake_id
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    res = book_model.create_book(
        title="Test Book",
        author=["Author"],
        page_count=123,
        genre="Genre",
        tags=["tag1"],
        publication_date="2025-01-01",
        isbn="isbn_123",
        isbn13="isbn13_123",
        cover_image="http://cover.jpg",
        language="en",
        publisher="Publisher",
        summary="Summary",
        genre_tags=["fiction"],
    )
    assert isinstance(res, str) and len(res) == 24  # Check ObjectId string length


def test_create_book_schema_validation(monkeypatch):
    # tags=None should trigger schema validation error
    monkeypatch.setattr(book_model, "books_collection", MagicMock())

    res = book_model.create_book(
        title="Bad Book",
        author=["Author"],
        page_count=123,
        genre="Genre",
        tags=None,  # invalid
        publication_date="2025-01-01",
        isbn="isbn_sch",
        isbn13="isbn13_sch",
        cover_image="",
        language="en",
        publisher="Publisher",
        summary="Summary",
        genre_tags=[],
    )
    assert res.startswith("Schema Validation Error:")


def test_create_book_invalid_date(monkeypatch):
    monkeypatch.setattr(book_model, "books_collection", MagicMock())

    res = book_model.create_book(
        title="Invalid Date",
        author=["Author"],
        page_count=123,
        genre="Genre",
        tags=["t"],
        publication_date="bad-date",  # invalid format
        isbn="invalid_date",
        isbn13="invalid_date13",
        cover_image="",
        language="en",
        publisher="Publisher",
        summary="Summary",
        genre_tags=[],
    )
    assert res == "Error: Invalid date format. Use YYYY-MM-DD."


def test_read_book_field_valid(mock_books_collection):
    assert book_model.read_book_field(mock_books_collection, "title") == "Mocked Book"


def test_read_book_field_invalid():
    assert (
        book_model.read_book_field("000000000000000000000000", "invalid_field")
        == "Book not found."
    )


def test_read_book_field_invalid_id():
    assert book_model.read_book_field("invalid_id", "title") == "Invalid book ID format"


def test_read_book_field_book_not_found():
    assert (
        book_model.read_book_field("000000000000000000000000", "title")
        == "Book not found."
    )


def test_read_book_field_schema_error(monkeypatch):
    # read_book_field does not use schema, so test for missing field instead
    incomplete_doc = {
        "_id": ObjectId(),
        "author": ["Author"],
        "page_count": 100,
        "genre": "Fiction",
    }
    monkeypatch.setattr(
        book_model, "books_collection", MagicMock(find_one=lambda q: incomplete_doc)
    )
    result = book_model.read_book_field(str(ObjectId()), "title")
    assert result == "Field not found"


def test_read_book_by_bookId_valid(mock_books_collection):
    assert (
        book_model.read_book_by_bookId(mock_books_collection)["title"] == "Mocked Book"
    )


def test_read_book_by_bookId_book_not_found():
    assert (
        book_model.read_book_by_bookId("000000000000000000000000") == "Book not found."
    )


def test_read_book_by_bookId_invalid_id_format():
    assert "Invalid book ID format" in book_model.read_book_by_bookId("temporary_id")


def test_read_book_by_bookId_schema_error(monkeypatch):
    monkeypatch.setattr(
        book_model,
        "books_collection",
        MagicMock(
            find_one=lambda q: {
                "_id": ObjectId(),
                "title": 123,
                "publication_date": "not-a-date",
            }
        ),
    )
    result = book_model.read_book_by_bookId(str(ObjectId()))
    assert result.startswith("Schema Validation Error:")


def test_read_book_by_identifier():
    assert book_model.read_book_by_identifier("mockisbn", "isbn") != "Book not found."


def test_read_book_by_identifier_invalid():
    assert book_model.read_book_by_identifier("invalid", "title") == "Book not found."


def test_read_book_by_identifier_invalid_identifier():
    assert (
        book_model.read_book_by_identifier("val", "foo")
        == "Error: Invalid identifier. Use 'title', 'isbn', or 'isbn13'."
    )


def test_read_book_by_identifier_schema_error(monkeypatch):
    monkeypatch.setattr(
        book_model,
        "books_collection",
        MagicMock(
            find_one=lambda q: {
                "_id": ObjectId(),
                "title": 123,
                "publication_date": "not-a-date",
            }
        ),
    )
    result = book_model.read_book_by_identifier("mockisbn", "isbn")
    assert result.startswith("Schema Validation Error:")


def test_read_book_title(mock_books_collection):
    assert book_model.read_book_title(mock_books_collection) == "Mocked Book"


def test_read_book_author(mock_books_collection):
    assert book_model.read_book_author(mock_books_collection) == ["Author"]


def test_read_book_page_count(mock_books_collection):
    assert book_model.read_book_page_count(mock_books_collection) == 100


def test_read_book_genre(mock_books_collection):
    assert book_model.read_book_genre(mock_books_collection) == "Fiction"


def test_read_book_tags(mock_books_collection):
    assert book_model.read_book_tags(mock_books_collection) == ["test"]


def test_read_book_publication_date(mock_books_collection):
    assert book_model.read_book_publication_date(mock_books_collection) == datetime(
        2025, 1, 1
    )


def test_read_book_isbn(mock_books_collection):
    assert book_model.read_book_isbn(mock_books_collection) == "mockisbn"


def test_read_book_isbn13(mock_books_collection):
    assert book_model.read_book_isbn13(mock_books_collection) == "mockisbn13"


def test_read_book_cover_image(mock_books_collection):
    assert (
        book_model.read_book_cover_image(mock_books_collection)
        == "http://example.com/image.jpg"
    )


def test_read_book_language(mock_books_collection):
    assert book_model.read_book_language(mock_books_collection) == "en"


def test_read_book_publisher(mock_books_collection):
    assert book_model.read_book_publisher(mock_books_collection) == "MockPub"


def test_read_book_summary(mock_books_collection):
    assert book_model.read_book_summary(mock_books_collection) == "Mock summary"


def test_read_book_genre_tags(mock_books_collection):
    assert book_model.read_book_genre_tags(mock_books_collection) == ["fiction"]


def test_update_book_details_success(monkeypatch, mock_books_collection):
    valid_doc = {
        "_id": ObjectId(mock_books_collection),
        "title": "Original Title",
        "author": ["Author"],
        "page_count": 100,
        "genre": "Fiction",
        "tags": ["test"],
        "publication_date": datetime(2025, 1, 1),
        "isbn": "mockisbn",
        "isbn13": "mockisbn13",
        "cover_image": "http://example.com/image.jpg",
        "language": "en",
        "publisher": "MockPub",
        "summary": "Mock summary",
        "genre_tags": ["fiction"],
        "embedding": [],
    }

    mock_col = MagicMock()
    mock_col.find_one.return_value = valid_doc
    mock_col.update_one.return_value.modified_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.update_book_details(
        str(valid_doc["_id"]), title="Updated Title"
    )
    assert result == "Book updated successfully."


def test_update_book_details_invalid_id():
    result = book_model.update_book_details("not-a-valid-id", title="Updated")
    assert result == "Error: Invalid ObjectId format."


def test_update_book_details_book_not_found(monkeypatch):
    mock_col = MagicMock()
    mock_col.find_one.return_value = None
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.update_book_details(str(ObjectId()), title="Updated")
    assert result == "Error: Book not found."


def test_update_book_details_validation_error(monkeypatch):
    valid_doc = {
        "_id": ObjectId(),
        "title": "T",
        "author": ["A"],
        "page_count": 1,
        "genre": "G",
        "tags": ["t"],
        "publication_date": "not-a-date",  # <- invalid
        "isbn": "x",
        "isbn13": "y",
        "cover_image": "",
        "language": "en",
        "publisher": "P",
        "summary": "S",
        "genre_tags": [],
        "embedding": [],
    }
    mock_col = MagicMock()
    mock_col.find_one.return_value = valid_doc
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.update_book_details(str(valid_doc["_id"]), title="Fails")
    assert result.startswith("Schema Validation Error:")


def test_add_book_author_success(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.add_book_author(fake_id, "New Author")
    assert result == "Author added successfully."


def test_add_book_author_already_exists(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 0
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.add_book_author(fake_id, "Existing Author")
    assert result == "Author was already in the list or book not found."


def test_add_book_author_invalid_id():
    result = book_model.add_book_author("bad-id", "Any Author")
    assert result == "Invalid book ID."


def test_add_book_author_empty_name():
    fake_id = str(ObjectId())
    result = book_model.add_book_author(fake_id, "")
    assert result == "Author name cannot be empty."


def test_add_book_tag_success(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.add_book_tag(fake_id, "New Tag")
    assert result == "Tag added successfully."


def test_add_book_tag_already_exists(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 0
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    result = book_model.add_book_tag(fake_id, "test")
    assert result == "Tag was already in the list or book not found."


def test_add_book_tag_invalid_id():
    result = book_model.add_book_tag("bad-id", "Some Tag")
    assert result == "Invalid book ID."


def test_add_book_tag_empty_name():
    fake_id = str(ObjectId())
    result = book_model.add_book_tag(fake_id, "")
    assert result == "Tag cannot be empty."


def test_remove_book_author_success(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    res = book_model.remove_book_author(fake_id, "Author")
    assert res == "Author removed successfully."


def test_remove_book_author_not_found(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 0
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    res = book_model.remove_book_author(fake_id, "Unknown Author")
    assert res == "Author not found in the list or book not found."


def test_remove_book_author_invalid_id():
    res = book_model.remove_book_author("bad", "Author")
    assert res == "Invalid book ID."


def test_remove_book_author_empty_name():
    fake_id = str(ObjectId())
    res = book_model.remove_book_author(fake_id, "")
    assert res == "Author name cannot be empty."


def test_remove_book_tag_success(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    res = book_model.remove_book_tag(fake_id, "tag")
    assert res == "Tag removed successfully."


def test_remove_book_tag_not_found(monkeypatch):
    fake_id = str(ObjectId())
    mock_col = MagicMock()
    mock_col.update_one.return_value.modified_count = 0
    monkeypatch.setattr(book_model, "books_collection", mock_col)

    res = book_model.remove_book_tag(fake_id, "missing")
    assert res == "Tag not found in the list or book not found."


def test_remove_book_tag_invalid_id():
    res = book_model.remove_book_tag("bad", "tag")
    assert res == "Invalid book ID."


def test_remove_book_tag_empty_name():
    fake_id = str(ObjectId())
    res = book_model.remove_book_tag(fake_id, "")
    assert res == "Tag cannot be empty."


def test_delete_book_success(monkeypatch):
    fake_id = ObjectId()

    mock_books = MagicMock()
    mock_books.find_one.return_value = {"_id": fake_id}
    mock_books.delete_one.return_value.deleted_count = 1

    mock_posts = MagicMock()
    mock_posts.find.return_value = [{"_id": ObjectId()}]
    mock_posts.delete_many.return_value = None

    mock_comments = MagicMock()
    mock_comments.delete_many.return_value = None

    mock_chats = MagicMock()
    mock_chats.delete_many.return_value = None

    mock_shelves = MagicMock()
    mock_shelves.delete_many.return_value = None

    mock_db = {
        "Books": mock_books,
        "Posts": mock_posts,
        "Comments": mock_comments,
        "Chat_Messages": mock_chats,
        "User_Bookshelf": mock_shelves,
    }

    monkeypatch.setattr(book_model, "collections", mock_db)
    monkeypatch.setattr(book_model, "books_collection", mock_books)

    result = book_model.delete_book(str(fake_id))
    assert result == "Book and related records deleted successfully."


def test_delete_book_not_found(monkeypatch):
    fake_id = ObjectId()

    mock_books = MagicMock()
    mock_books.find_one.return_value = None
    monkeypatch.setattr(book_model, "books_collection", mock_books)

    result = book_model.delete_book(str(fake_id))
    assert result == "Error: Book not found."


def test_delete_book_invalid_id():
    result = book_model.delete_book("notanid")
    assert result == "Invalid book ID format"
