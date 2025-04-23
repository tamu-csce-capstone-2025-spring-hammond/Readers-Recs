import pytest
from main import app
import uuid
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from unittest.mock import patch
from bson.objectid import ObjectId

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user_book():
    fake_user_id = str(ObjectId())
    fake_book_id = str(ObjectId())
    with patch("models.users.create_user", return_value=fake_user_id), patch(
        "models.books.create_book", return_value=fake_book_id
    ), patch("models.users.delete_user"), patch("models.books.delete_book"):
        yield fake_user_id, fake_book_id


def test_create_post_missing_fields(client):
    response = client.post("/api/books/invalid_id/posts", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_post_invalid_user(client):
    with patch("api.posts.create_post", return_value="Error: Invalid user_id."):
        response = client.post(
            "/api/books/invalid_id/posts",
            json={
                "user_id": "baduser",
                "title": "Test Title",
                "post_text": "Some text",
            },
        )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_posts_invalid_book(client):
    with patch(
        "api.posts.get_all_posts_for_book", return_value="Error: Invalid book_id."
    ):
        response = client.get("/api/books/invalid_id/posts")
    assert response.status_code in [400, 500]
    assert "error" in response.get_json()


def test_create_post_valid(client, valid_user_book):
    user_id, book_id = valid_user_book
    fake_post_id = str(ObjectId())

    with patch("api.posts.create_post", return_value=fake_post_id):
        response = client.post(
            f"/api/books/{book_id}/posts",
            json={
                "user_id": user_id,
                "title": "A valid post",
                "post_text": "Here’s something worth discussing!",
                "tags": ["tag1", "tag2"],
            },
        )

    assert response.status_code == 201
    data = response.get_json()
    assert "post_id" in data
    assert data["post_id"] == fake_post_id


def test_get_all_posts_valid(client, valid_user_book):
    user_id, book_id = valid_user_book
    fake_post_id = str(ObjectId())
    fake_posts = [
        {
            "_id": fake_post_id,
            "user_id": user_id,
            "book_id": book_id,
            "title": "Post #1",
            "post_text": "More discussion",
            "tags": ["test"],
            "username": "mockuser",
            "profile_picture": "",
        },
        {
            "_id": str(ObjectId()),
            "user_id": user_id,
            "book_id": book_id,
            "title": "Post #2",
            "post_text": "More discussion",
            "tags": ["test"],
            "username": "mockuser",
            "profile_picture": "",
        },
    ]

    with patch("api.posts.create_post", return_value=fake_post_id), patch(
        "api.posts.get_all_posts_for_book", return_value=fake_posts
    ):

        for i in range(2):
            client.post(
                f"/api/books/{book_id}/posts",
                json={
                    "user_id": user_id,
                    "title": f"Post #{i+1}",
                    "post_text": "More discussion",
                    "tags": ["test"],
                },
            )

        response = client.get(f"/api/books/{book_id}/posts")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_create_post_internal_error(client, valid_user_book):
    user_id, book_id = valid_user_book

    with patch("api.posts.create_post", side_effect=Exception("Create failure")):
        response = client.post(
            f"/api/books/{book_id}/posts",
            json={
                "user_id": user_id,
                "title": "Post",
                "post_text": "Crash",
            },
        )

    assert response.status_code == 500
    assert "Create failure" in response.get_json()["error"]


def test_get_all_posts_internal_error(client, valid_user_book):
    _, book_id = valid_user_book

    with patch("api.posts.get_all_posts_for_book", side_effect=Exception("Boom")):
        response = client.get(f"/api/books/{book_id}/posts")

    assert response.status_code == 500
    assert "Boom" in response.get_json()["error"]
