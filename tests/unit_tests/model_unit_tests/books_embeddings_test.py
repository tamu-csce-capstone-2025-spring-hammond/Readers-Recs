import pytest
import numpy as np
from bson import ObjectId
from unittest.mock import MagicMock
import models.books as book_model


@pytest.fixture
def mock_books(monkeypatch):
    fake_id = str(ObjectId())

    # Fake existing document
    fake_doc = {"_id": ObjectId(fake_id), "embedding": []}

    # Patch find_one and update_one
    mock_collection = MagicMock()
    mock_collection.find_one.side_effect = lambda query: (
        fake_doc if query["_id"] == ObjectId(fake_id) else None
    )

    def mock_update_one(filter_, update_):
        # Simulate a change
        new_embedding = update_["$set"]["embedding"]
        if new_embedding != fake_doc["embedding"]:
            fake_doc["embedding"] = new_embedding
            return MagicMock(modified_count=1)
        return MagicMock(modified_count=0)

    mock_collection.update_one.side_effect = mock_update_one
    monkeypatch.setattr(book_model, "books_collection", mock_collection)

    return fake_id


def test_invalid_book_id():
    assert (
        book_model.update_book_embedding("not_a_valid_id", [0.1, 0.2])
        == "Invalid book ID."
    )


def test_invalid_embedding_type(mock_books):
    for bad in ("string", 123, {"a": 1}, None):
        assert (
            book_model.update_book_embedding(mock_books, bad)
            == "Embedding must be a list or NumPy array."
        )


def test_success_with_list(mock_books):
    emb = [1.0, 2.0, 3.0]
    res = book_model.update_book_embedding(mock_books, emb)
    assert res == "Embedding updated successfully."


def test_success_with_ndarray(mock_books):
    arr = np.array([4.0, 5.0])
    res = book_model.update_book_embedding(mock_books, arr)
    assert res == "Embedding updated successfully."


def test_unchanged_embedding(mock_books):
    emb = [7.7, 8.8]
    assert (
        book_model.update_book_embedding(mock_books, emb)
        == "Embedding updated successfully."
    )
    res2 = book_model.update_book_embedding(mock_books, emb)
    assert res2 == "Book not found or embedding unchanged."


def test_book_not_found_valid_id(monkeypatch):
    fake_id = str(ObjectId())

    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None  # Book not found
    mock_collection.update_one.return_value = MagicMock(modified_count=0)

    monkeypatch.setattr(book_model, "books_collection", mock_collection)

    res = book_model.update_book_embedding(fake_id, [9.9])
    assert res == "Book not found or embedding unchanged."


def test_empty_list_embedding(mock_books):
    res = book_model.update_book_embedding(mock_books, [])
    assert res == "Book not found or embedding unchanged."


def test_empty_list_after_nonempty(mock_books):
    assert (
        book_model.update_book_embedding(mock_books, [0.5, 0.6])
        == "Embedding updated successfully."
    )
    res = book_model.update_book_embedding(mock_books, [])
    assert res == "Embedding updated successfully."
