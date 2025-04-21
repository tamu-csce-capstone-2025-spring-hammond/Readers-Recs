import pytest
from main import app

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_search_books_valid_query(client):
    response = client.get("/api/books?query=Harry")
    assert response.status_code in [200, 404]
    assert isinstance(response.get_json(), list) or "error" in response.get_json()


def test_search_books_missing_query(client):
    response = client.get("/api/books")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Query parameter is required"


def test_search_books_by_author(client):
    response = client.get("/api/books?query=Rowling&type=author")
    assert response.status_code in [200, 404]
