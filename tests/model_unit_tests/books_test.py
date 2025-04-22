import pytest
import uuid
from unittest.mock import MagicMock
from bson import ObjectId
import models.books as book_model

# Patch books_collection globally
@pytest.fixture(autouse=True)
def mock_books_collection(monkeypatch):
    fake_id = ObjectId()
    fake_doc = {
        "_id": fake_id,
        "title": "Mocked Book",
        "author": ["Author"],
        "page_count": 100,
        "genre": "Fiction",
        "tags": ["test"],
        "publication_date": "2025-01-01",
        "isbn": "mockisbn",
        "isbn13": "mockisbn13",
        "cover_image": "http://example.com/image.jpg",
        "language": "en",
        "publisher": "MockPub",
        "summary": "Mock summary",
        "genre_tags": ["fiction"],
        "embedding": []
    }

    mock_col = MagicMock()
    mock_col.insert_one.return_value.inserted_id = fake_id
    mock_col.find_one.side_effect = lambda q, *args, **kwargs: fake_doc if ("_id" in q and q["_id"] == fake_id) or ("isbn" in q and q["isbn"] == "mockisbn") or ("title" in q and q["title"] == "Mocked Book") or ("isbn13" in q and q["isbn13"] == "mockisbn13") else None
    mock_col.update_one.return_value.modified_count = 1
    mock_col.delete_one.return_value.deleted_count = 1
    monkeypatch.setattr(book_model, "books_collection", mock_col)
    return str(fake_id)

def test_read_book_field_valid(mock_books_collection):
    assert book_model.read_book_field(mock_books_collection, "title") == "Mocked Book"

def test_read_book_field_invalid():
    assert book_model.read_book_field("000000000000000000000000", "invalid_field") == "Book not found."

def test_read_book_field_invalid_id():
    assert book_model.read_book_field("invalid_id", "title") == "Invalid book ID format"

def test_read_book_field_book_not_found():
    assert book_model.read_book_field("000000000000000000000000", "title") == "Book not found."

def test_read_book_field_schema_error(monkeypatch):
    monkeypatch.setattr(book_model, "books_collection", MagicMock(find_one=lambda q: {"_id": ObjectId(), "publication_date": "not-a-date"}))
    result = book_model.read_book_field(str(ObjectId()), "title")
    assert result.startswith("Schema Validation Error:")

def test_read_book_by_bookId_valid(mock_books_collection):
    assert book_model.read_book_by_bookId(mock_books_collection)["title"] == "Mocked Book"

def test_read_book_by_bookId_book_not_found():
    assert book_model.read_book_by_bookId("000000000000000000000000") == "Book not found."

def test_read_book_by_bookId_invalid_id_format():
    assert "Invalid book ID format" in book_model.read_book_by_bookId("temporary_id")

def test_read_book_by_bookId_schema_error(monkeypatch):
    monkeypatch.setattr(book_model, "books_collection", MagicMock(find_one=lambda q: {"_id": ObjectId(), "publication_date": "not-a-date"}))
    result = book_model.read_book_by_bookId(str(ObjectId()))
    assert result.startswith("Schema Validation Error:")

def test_read_book_by_identifier():
    assert book_model.read_book_by_identifier("mockisbn", "isbn") != "Book not found."

def test_read_book_by_identifier_invalid():
    assert book_model.read_book_by_identifier("invalid", "title") == "Book not found."

def test_read_book_by_identifier_invalid_identifier():
    assert book_model.read_book_by_identifier("val", "foo") == "Error: Invalid identifier. Use 'title', 'isbn', or 'isbn13'."

def test_read_book_by_identifier_schema_error(monkeypatch):
    monkeypatch.setattr(book_model, "books_collection", MagicMock(find_one=lambda q: {"_id": ObjectId(), "publication_date": "not-a-date"}))
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
    assert book_model.read_book_publication_date(mock_books_collection) == "2025-01-01"

def test_read_book_isbn(mock_books_collection):
    assert book_model.read_book_isbn(mock_books_collection) == "mockisbn"

def test_read_book_isbn13(mock_books_collection):
    assert book_model.read_book_isbn13(mock_books_collection) == "mockisbn13"

def test_read_book_cover_image(mock_books_collection):
    assert book_model.read_book_cover_image(mock_books_collection) == "http://example.com/image.jpg"

def test_read_book_language(mock_books_collection):
    assert book_model.read_book_language(mock_books_collection) == "en"

def test_read_book_publisher(mock_books_collection):
    assert book_model.read_book_publisher(mock_books_collection) == "MockPub"

def test_read_book_summary(mock_books_collection):
    assert book_model.read_book_summary(mock_books_collection) == "Mock summary"

def test_read_book_genre_tags(mock_books_collection):
    assert book_model.read_book_genre_tags(mock_books_collection) == ["fiction"]

def test_update_book_details_success(mock_books_collection):
    res = book_model.update_book_details(mock_books_collection, title="New Title")
    assert res == "Book updated successfully."

def test_update_book_details_invalid_format():
    res = book_model.update_book_details("nothex", title="fail")
    assert res == "Error: Invalid ObjectId format."

def test_update_book_details_not_found():
    res = book_model.update_book_details("000000000000000000000000", title="fail")
    assert res == "Error: Book not found."

def test_add_book_author_invalid():
    assert book_model.add_book_author("badid", "Author") == "Invalid book ID."

def test_add_book_author_empty(mock_books_collection):
    assert book_model.add_book_author(mock_books_collection, "") == "Author name cannot be empty."

def test_add_book_author_success(mock_books_collection):
    assert book_model.add_book_author(mock_books_collection, "New Author") == "Author added successfully."

def test_add_book_tag_invalid():
    assert book_model.add_book_tag("badid", "tag") == "Invalid book ID."

def test_add_book_tag_empty(mock_books_collection):
    assert book_model.add_book_tag(mock_books_collection, "") == "Tag cannot be empty."

def test_add_book_tag_success(mock_books_collection):
    assert book_model.add_book_tag(mock_books_collection, "New Tag") == "Tag added successfully."

def test_remove_book_author_empty(mock_books_collection):
    assert book_model.remove_book_author(mock_books_collection, "") == "Author name cannot be empty."

def test_remove_book_author_success(mock_books_collection):
    assert book_model.remove_book_author(mock_books_collection, "Author") == "Author removed successfully."

def test_remove_book_tag_empty(mock_books_collection):
    assert book_model.remove_book_tag(mock_books_collection, "") == "Tag cannot be empty."

def test_remove_book_tag_success(mock_books_collection):
    assert book_model.remove_book_tag(mock_books_collection, "test") == "Tag removed successfully."

def test_delete_book_invalid():
    assert book_model.delete_book("not-an-id") == "Invalid book ID format"

def test_delete_book_not_found():
    assert book_model.delete_book("000000000000000000000000") == "Error: Book not found."

def test_delete_book_success(mock_books_collection):
    assert book_model.delete_book(mock_books_collection) == "Book and related records deleted successfully."

def test_create_book_value_error():
    result = book_model.create_book("T", ["A"], 1, "G", ["t"], "bad-date", "x", "y", "", "en", "P", "S", [])
    assert result == "Error: Invalid date format. Use YYYY-MM-DD."

def test_create_book_schema_validation_error():
    result = book_model.create_book("T", ["A"], 1, "G", None, "2025-01-01", "x", "y", "", "en", "P", "S", [])
    assert result.startswith("Schema Validation Error:")
