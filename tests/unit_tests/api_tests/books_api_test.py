import pytest
from main import app
from unittest.mock import patch

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_search_books_valid_query(client):
    mock_result = [
        {"title": "Harry Potter", "author": ["J.K. Rowling"], "isbn": "123456789"}
    ]

    with patch("api.books.search_books", return_value=mock_result):  # update if needed
        response = client.get("/api/books?query=Harry")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert response.get_json()[0]["title"].startswith("Harry Potter")


def test_search_books_missing_query(client):
    response = client.get("/api/books")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Query parameter is required"


def test_search_books_by_author(client):
    mock_books = [
        {"title": "Fantastic Beasts", "author": ["J.K. Rowling"], "isbn": "987654321"}
    ]

    with patch("api.books.search_books", return_value=mock_books):  # update if needed
        response = client.get("/api/books?query=Rowling&type=author")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert "J.K. Rowling" in response.get_json()[0]["author"]
