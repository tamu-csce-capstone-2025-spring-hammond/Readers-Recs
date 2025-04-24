import pytest
from unittest.mock import patch
from bson import ObjectId
from main import app
from models.comments import serialize_comment
from datetime import datetime

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user_post():
    user_id = str(ObjectId())
    post_id = str(ObjectId())

    mock_user = {
        "_id": ObjectId(user_id),
        "first_name": "T",
        "last_name": "U",
        "username": "mockuser",
        "email_address": "mock@example.com",
        "oauth": {"access_token": "tok", "refresh_token": "tok"},
        "profile_image": "",
        "interests": [],
        "demographics": {},
        "genre_weights": {},
        "embedding": [],
    }

    mock_post = {
        "_id": ObjectId(post_id),
        "user_id": ObjectId(user_id),
        "book_id": ObjectId(),
        "title": "Mock Post",
        "content": "Text",
        "tags": ["tag"],
    }

    with patch("models.users.read_user", return_value=mock_user), patch(
        "models.posts.read_post", return_value=mock_post
    ), patch("models.users.is_valid_object_id", return_value=True), patch(
        "models.posts.is_valid_object_id", return_value=True
    ):
        yield user_id, post_id


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
            "comment_text": 123,
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


def test_add_comment_forced_exception(client):
    with patch(
        "api.comments.create_initial_comment", side_effect=Exception("boom")
    ), patch("models.comments.is_valid_object_id", return_value=True):
        response = client.post(
            "/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments",
            json={"user_id": "bbbbbbbbbbbbbbbbbbbbbbbb", "comment_text": "Hello"},
        )
        assert response.status_code == 500
        assert "boom" in response.get_json()["error"]


def test_reply_comment_internal_error(client):
    with patch(
        "api.comments.reply_to_comment", side_effect=Exception("Reply failure")
    ), patch("models.comments.is_valid_object_id", return_value=True):
        response = client.post(
            "/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments/cccccccccccccccccccccccc/reply",
            json={"user_id": "bbbbbbbbbbbbbbbbbbbbbbbb", "comment_text": "reply"},
        )
        assert response.status_code == 500
        assert "Reply failure" in response.get_json()["error"]


def test_get_all_comments_internal_error(client):
    with patch(
        "api.comments.get_all_comments_for_post", side_effect=Exception("Crash")
    ), patch("models.comments.is_valid_object_id", return_value=True):
        response = client.get("/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments")
        assert response.status_code == 500
        assert "Crash" in response.get_json()["error"]


def test_get_single_comment_internal_error(client):
    with patch(
        "api.comments.read_comment", side_effect=Exception("Boom on read")
    ), patch("models.comments.is_valid_object_id", return_value=True):
        response = client.get(
            "/api/posts/aaaaaaaaaaaaaaaaaaaaaaaa/comments/dddddddddddddddddddddddd"
        )
        assert response.status_code == 500
        assert "Boom on read" in response.get_json()["error"]


def test_create_comment_valid(client, valid_user_post):
    user_id, post_id = valid_user_post

    with patch(
        "api.comments.create_initial_comment", return_value=str(ObjectId())
    ), patch("models.comments.is_valid_object_id", return_value=True):
        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"user_id": user_id, "comment_text": "This is a valid comment"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "comment_id" in data


def test_reply_to_comment_valid(client, valid_user_post):
    user_id, post_id = valid_user_post
    fake_comment_id = str(ObjectId())

    with patch(
        "api.comments.create_initial_comment", return_value=str(ObjectId())
    ), patch("api.comments.reply_to_comment", return_value=fake_comment_id), patch(
        "models.comments.is_valid_object_id", return_value=True
    ):
        # Create top-level comment
        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"user_id": user_id, "comment_text": "Top-level comment"},
        )
        assert response.status_code == 201
        parent_comment_id = response.get_json()["comment_id"]

        # Reply
        reply = client.post(
            f"/api/posts/{post_id}/comments/{parent_comment_id}/reply",
            json={"user_id": user_id, "comment_text": "This is a reply"},
        )
        assert reply.status_code == 201
        assert "comment_id" in reply.get_json()
