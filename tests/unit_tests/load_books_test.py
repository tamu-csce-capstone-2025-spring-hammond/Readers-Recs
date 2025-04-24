import json
import os
import pytest
from unittest.mock import patch, mock_open
from load_books import BookCollection
from bson import ObjectId
from datetime import datetime
import threading
import time


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=json.dumps(
        [
            {
                "_id": str(ObjectId()),
                "title": "Test Book",
                "publication_date": "2024-01-01T00:00:00",
            }
        ]
    ),
)
@patch("os.path.exists", return_value=True)
def test_load_books_from_cache(mock_exists, mock_file):
    bc = BookCollection(cache_file="test_books_cache.json")
    assert len(bc.books) == 1
    assert isinstance(bc.books[0]["_id"], ObjectId)
    assert isinstance(bc.books[0]["publication_date"], datetime)


@patch(
    "load_books.books_collection.find",
    return_value=[{"_id": ObjectId(), "publication_date": datetime.now()}],
)
@patch("os.path.exists", return_value=False)
def test_refresh_books_triggers_on_init(mock_exists, mock_find):
    bc = BookCollection(cache_file="test_books_cache.json")
    assert isinstance(bc.books, list)
    assert len(bc.books) > 0


def test_get_books_returns_copy():
    bc = BookCollection(cache_file="test_books_cache.json")
    books = bc.get_books()

    # Should be a different object, but with same contents
    assert books == bc.books
    assert books is not bc.books  # Ensure it's a copy


@patch("load_books.BookCollection.refresh_books")
@patch("time.sleep", side_effect=InterruptedError)  # Break the loop immediately
def test_refresh_loop_triggers_refresh(mock_sleep, mock_refresh):
    bc = BookCollection(cache_file="test_books_cache.json")

    # Run loop in a separate thread, catch the early break
    def run_loop():
        try:
            bc._refresh_loop()
        except InterruptedError:
            pass

    thread = threading.Thread(target=run_loop)
    thread.start()
    thread.join(timeout=2)

    mock_sleep.assert_called_once_with(bc.refresh_interval)
