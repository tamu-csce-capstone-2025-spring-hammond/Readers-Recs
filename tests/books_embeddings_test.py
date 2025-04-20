import pytest
import uuid
import numpy as np
from bson import ObjectId
from backend.models.books import (
    create_book,
    delete_book,
    update_book_embedding,
)
from backend.database import collections

books_collection = collections["Books"]


@pytest.fixture
def book_id():
    # Create a fresh book to test against
    isbn = uuid.uuid4().hex[:9]
    isbn13 = uuid.uuid4().hex[:13]
    bid = create_book(
        title="Embed Test",
        author=["Author"],
        page_count=10,
        genre="Test",
        tags=["tag"],
        publication_date="2025-01-01",
        isbn=isbn,
        isbn13=isbn13,
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["genre"],
    )
    yield bid
    # Cleanup
    delete_book(bid)


def test_invalid_book_id():
    assert update_book_embedding("not_a_valid_id", [0.1, 0.2]) == "Invalid book ID."


def test_invalid_embedding_type(book_id):
    for bad in ("string", 123, {"a": 1}, None):
        assert (
            update_book_embedding(book_id, bad)
            == "Embedding must be a list or NumPy array."
        )


def test_success_with_list(book_id):
    emb = [1.0, 2.0, 3.0]
    res = update_book_embedding(book_id, emb)
    assert res == "Embedding updated successfully."
    doc = books_collection.find_one({"_id": ObjectId(book_id)})
    assert doc["embedding"] == emb


def test_success_with_ndarray(book_id):
    arr = np.array([4.0, 5.0])
    res = update_book_embedding(book_id, arr)
    assert res == "Embedding updated successfully."
    doc = books_collection.find_one({"_id": ObjectId(book_id)})
    assert doc["embedding"] == [4.0, 5.0]


def test_unchanged_embedding(book_id):
    emb = [7.7, 8.8]
    # First write succeeds
    assert update_book_embedding(book_id, emb) == "Embedding updated successfully."
    # Second write with identical list is a no-op
    res2 = update_book_embedding(book_id, emb)
    assert res2 == "Book not found or embedding unchanged."


def test_book_not_found_valid_id():
    fake = str(ObjectId())
    res = update_book_embedding(fake, [9.9])
    assert res == "Book not found or embedding unchanged."


def test_empty_list_embedding(book_id):
    # Default embedding is an empty list, so no change
    res = update_book_embedding(book_id, [])
    assert res == "Book not found or embedding unchanged."


def test_empty_list_after_nonempty(book_id):
    # First set a non-empty embedding
    assert (
        update_book_embedding(book_id, [0.5, 0.6]) == "Embedding updated successfully."
    )
    # Now clearing it to empty should succeed
    res = update_book_embedding(book_id, [])
    assert res == "Embedding updated successfully."
    doc = books_collection.find_one({"_id": ObjectId(book_id)})
    assert doc["embedding"] == []
