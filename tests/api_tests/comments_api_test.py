import pytest
from main import app
from bson import ObjectId
from models.comments import serialize_comment
from datetime import datetime
import uuid
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.posts import create_post, delete_post

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user_post():
    u = uuid.uuid4().hex
    user_id = create_user(
        first_name="T",
        last_name="U",
        username=f"user_{u}",
        email_address=f"{u}@test.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    book_id = create_book(
        title="Book for Comments",
        author=["Author"],
        page_count=123,
        genre="Test",
        tags=["tag"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["fiction"],
    )
    post_id = create_post(user_id, book_id, "Commentable Post", "Text", ["tag"])

    yield user_id, post_id

    delete_post(post_id)
    delete_user(user_id)
    delete_book(book_id)


# -------------------------------
# CREATE COMMENT TESTS
# -------------------------------
def test_create_comment_missing_fields(client):
    response = client.post("/api/posts/invalid_id/comments", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_comment_invalid_user(client):
    response = client.post(
        "/api/posts/invalid_id/comments",
        json={"user_id": "not_real", "comment_text": "This should fail"},
    )
    assert response.status_code == 400


def test_create_comment_invalid_post(client):
    response = client.post(
        "/api/posts/000000000000000000000000/comments",
        json={
            "user_id": "000000000000000000000000",
            "comment_text": "Will fail because post doesn't exist",
        },
    )
    assert response.status_code in [400, 404]


# -------------------------------
# REPLY TO COMMENT TESTS
# -------------------------------
def test_reply_to_comment_invalid_ids(client):
    response = client.post(
        "/api/posts/invalid_id/comments/invalid_comment_id/reply",
        json={"user_id": "baduser", "comment_text": "Reply"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_reply_to_comment_missing_fields(client):
    response = client.post(
        "/api/posts/invalid_id/comments/invalid_comment_id/reply", json={}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


# -------------------------------
# READ COMMENT TESTS
# -------------------------------
def test_get_comment_invalid_id(client):
    response = client.get("/api/posts/invalid_id/comments/invalid_comment_id")
    assert response.status_code in [400, 404]
    assert "error" in response.get_json()


def test_create_comment_validation_error(client):
    response = client.post(
        "/api/posts/invalid_id/comments",
        json={
            "user_id": "000000000000000000000000",
            "comment_text": 123,  # invalid type
        },
    )
    assert response.status_code in [400, 422]


def test_read_comment_field_not_found_doc(client):
    response = client.get(
        "/api/posts/000000000000000000000000/comments/000000000000000000000000/field/nonexistent"
    )
    assert response.status_code in [404, 400]


def test_get_all_comments_empty_list(client):
    response = client.get("/api/posts/000000000000000000000000/comments")
    assert response.status_code in [400, 404]
    assert "error" in response.get_json()


def test_serialize_comment_with_nulls():
    comment = {
        "_id": ObjectId(),
        "post_id": ObjectId(),
        "user_id": ObjectId(),
        "comment_text": "test",
        "parent_comment_id": None,
        "date_posted": datetime.now(),
        "date_edited": datetime.now(),
    }
    result = serialize_comment(comment)
    assert result["content"] == "test"
    assert result["parent_comment_id"] is None


def test_add_comment_forced_exception(monkeypatch, client):
    def force_crash(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr("api.comments.create_initial_comment", force_crash)
    monkeypatch.setattr("models.comments.is_valid_object_id", lambda c, x: True)

    response = client.post(
        "/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments",
        json={"user_id": "bbbbbbbbbbbbbbbbbbbbbbbb", "comment_text": "Hello"},
    )
    assert response.status_code == 500
    assert "boom" in response.get_json()["error"]


def test_reply_comment_internal_error(monkeypatch, client):
    def boom(*args, **kwargs):
        raise Exception("Reply failure")

    monkeypatch.setattr("api.comments.reply_to_comment", boom)
    monkeypatch.setattr("models.comments.is_valid_object_id", lambda c, x: True)

    response = client.post(
        "/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments/cccccccccccccccccccccccc/reply",
        json={"user_id": "bbbbbbbbbbbbbbbbbbbbbbbb", "comment_text": "reply"},
    )
    assert response.status_code == 500
    assert "Reply failure" in response.get_json()["error"]


def test_get_all_comments_internal_error(monkeypatch, client):
    def crash(_):
        raise Exception("Crash")

    monkeypatch.setattr("api.comments.get_all_comments_for_post", crash)
    monkeypatch.setattr("models.comments.is_valid_object_id", lambda c, x: True)

    response = client.get("/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments")
    assert response.status_code == 500
    assert "Crash" in response.get_json()["error"]


def test_get_single_comment_internal_error(monkeypatch, client):
    def boom(_):
        raise Exception("Boom on read")

    monkeypatch.setattr("api.comments.read_comment", boom)
    monkeypatch.setattr("models.comments.is_valid_object_id", lambda c, x: True)

    response = client.get(
        "/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments/dddddddddddddddddddddddd"
    )
    assert response.status_code == 500
    assert "Boom on read" in response.get_json()["error"]


def test_create_comment_valid(client, valid_user_post):
    user_id, post_id = valid_user_post

    response = client.post(
        f"/api/posts/{post_id}/comments",
        json={"user_id": user_id, "comment_text": "This is a valid comment"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "comment_id" in data


def test_reply_to_comment_valid(client, valid_user_post):
    user_id, post_id = valid_user_post

    # First create a top-level comment
    response = client.post(
        f"/api/posts/{post_id}/comments",
        json={"user_id": user_id, "comment_text": "Top-level comment"},
    )
    parent_comment_id = response.get_json()["comment_id"]

    # Then reply to it
    reply = client.post(
        f"/api/posts/{post_id}/comments/{parent_comment_id}/reply",
        json={"user_id": user_id, "comment_text": "This is a reply"},
    )
    assert reply.status_code == 201
    data = reply.get_json()
    assert "comment_id" in data


def test_get_all_comments_valid(client, valid_user_post):
    user_id, post_id = valid_user_post

    client.post(
        f"/api/posts/{post_id}/comments",
        json={"user_id": user_id, "comment_text": "First comment"},
    )
    client.post(
        f"/api/posts/{post_id}/comments",
        json={"user_id": user_id, "comment_text": "Second comment"},
    )

    response = client.get(f"/api/posts/{post_id}/comments")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
