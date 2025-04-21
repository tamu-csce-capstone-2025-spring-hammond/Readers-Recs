import pytest
from main import app
import uuid
from models.users import create_user, delete_user
from models.books import create_book, delete_book

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_user_book():
    u = uuid.uuid4().hex
    user_id = create_user(
        first_name="Posty",
        last_name="User",
        username=f"postuser_{u}",
        email_address=f"{u}@test.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={}
    )
    book_id = create_book(
        title="Postable Book",
        author=["Author"],
        page_count=222,
        genre="Fiction",
        tags=["discussion"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["fiction"]
    )
    yield user_id, book_id
    delete_user(user_id)
    delete_book(book_id)

def test_create_post_missing_fields(client):
    response = client.post("/api/books/invalid_id/posts", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_post_invalid_user(client):
    response = client.post(
        "/api/books/invalid_id/posts",
        json={"user_id": "baduser", "title": "Test Title", "post_text": "Some text"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_posts_invalid_book(client):
    response = client.get("/api/books/invalid_id/posts")
    assert response.status_code in [400, 500]
    assert "error" in response.get_json()

def test_create_post_valid(client, valid_user_book):
    user_id, book_id = valid_user_book
    response = client.post(f"/api/books/{book_id}/posts", json={
        "user_id": user_id,
        "title": "A valid post",
        "post_text": "Here’s something worth discussing!",
        "tags": ["tag1", "tag2"]
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "post_id" in data

def test_get_all_posts_valid(client, valid_user_book):
    user_id, book_id = valid_user_book

    # Create two posts
    for i in range(2):
        client.post(f"/api/books/{book_id}/posts", json={
            "user_id": user_id,
            "title": f"Post #{i+1}",
            "post_text": "More discussion",
            "tags": ["test"]
        })

    response = client.get(f"/api/books/{book_id}/posts")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_create_post_internal_error(monkeypatch, client, valid_user_book):
    from api import posts

    def boom(*args, **kwargs):
        raise Exception("Create failure")

    monkeypatch.setattr("api.posts.create_post", boom)

    user_id, book_id = valid_user_book
    response = client.post(f"/api/books/{book_id}/posts", json={
        "user_id": user_id,
        "title": "Post",
        "post_text": "Crash",
    })
    assert response.status_code == 500
    assert "Create failure" in response.get_json()["error"]

def test_get_all_posts_internal_error(monkeypatch, client, valid_user_book):
    from api import posts

    def crash(book_id):
        raise Exception("Boom")

    monkeypatch.setattr("api.posts.get_all_posts_for_book", crash)

    _, book_id = valid_user_book
    response = client.get(f"/api/books/{book_id}/posts")
    assert response.status_code == 500
    assert "Boom" in response.get_json()["error"]

