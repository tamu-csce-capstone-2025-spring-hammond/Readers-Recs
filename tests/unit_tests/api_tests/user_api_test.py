import pytest
import uuid
from bson import ObjectId
from main import app
from unittest.mock import patch, MagicMock

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user(request):
    user_id = str(ObjectId())
    email = f"{uuid.uuid4().hex}@test.com"

    with patch("models.users.create_user", return_value=user_id), patch(
        "models.users.delete_user"
    ) as delete_mock:
        request.addfinalizer(lambda: delete_mock(user_id))
        yield user_id, email


# ---------------- GET /user/profile/<user_id> ---------------- #


def test_get_user_profile_valid(client):
    mock_user = {
        "_id": ObjectId(),
        "first_name": "Test",
        "last_name": "User",
        "username": "mockuser",
        "profile_image": "mock.jpg",
        "interests": [],
        "demographics": {},
        "email_address": "mock@example.com",
        "oauth": {"access_token": "token", "refresh_token": "token"},
    }

    with patch("models.users.users_collection.find_one", return_value=mock_user):
        res = client.get(f"/user/profile/{mock_user['_id']}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["id"] == str(mock_user["_id"])
        assert data["name"] == "Test User"
        assert data["profile_picture"] == "mock.jpg"


def test_get_user_profile_invalid_format(client):
    res = client.get("/user/profile/notavalidid")
    assert res.status_code == 404
    assert "Invalid ObjectId format" in res.get_json()["error"]


def test_get_user_profile_not_found(client):
    fake_id = str(ObjectId())
    res = client.get(f"/user/profile/{fake_id}")
    assert res.status_code == 404
    assert "User not found" in res.get_json()["error"]


def test_get_user_profile_blank_fields(client):
    mock_user = {
        "_id": ObjectId(),
        "first_name": "",
        "last_name": "",
        "username": "blank",
        "profile_image": "",
        "interests": [],
        "demographics": {},
        "email_address": "blank@example.com",
        "oauth": {},
    }

    with patch("models.users.users_collection.find_one", return_value=mock_user):
        res = client.get(f"/user/profile/{mock_user['_id']}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["name"] == ""
        assert data["profile_picture"] == ""


# ---------------- POST /user/profile/<user_id>/edit-profile ---------------- #


def test_edit_profile_valid(client):
    fake_id = str(ObjectId())

    with patch(
        "api.user.update_user_settings", return_value="Profile updated successfully."
    ):
        response = client.post(
            f"/user/profile/{fake_id}/edit-profile",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "username": f"updated_user_{fake_id[:5]}",
                "profile_image": "new_pic.jpg",
            },
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Profile updated successfully."


def test_edit_profile_invalid_user_id(client):
    response = client.post("/user/profile/invalid_id/edit-profile", json={})
    assert response.status_code in [400, 404]
    assert "error" in response.get_json()


def test_edit_profile_crash(monkeypatch, client, valid_user):

    def explode(*args, **kwargs):
        raise Exception("Boom")

    monkeypatch.setattr("api.user.update_user_settings", explode)

    user_id, _ = valid_user
    response = client.post(
        f"/user/profile/{user_id}/edit-profile", json={"first_name": "Crash"}
    )
    assert response.status_code == 500
    assert "Boom" in response.get_json()["error"]


# ---------------- POST /user/save-genres ---------------- #


def test_save_genres_missing_auth(client):
    response = client.post("/user/save-genres", json={"genres": ["fantasy"]})
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_save_genres_invalid_payload(client):
    headers = {"Authorization": "Bearer fake_token"}
    response = client.post("/user/save-genres", json={}, headers=headers)
    assert response.status_code in [400, 401, 404]


# ---------------- GET /user/check-email-exists ---------------- #


def test_check_email_exists_missing_param(client):
    response = client.get("/user/check-email-exists")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_check_email_exists_nonexistent(client):
    with patch("models.users.users_collection.find_one", return_value=None):
        response = client.get("/user/check-email-exists?email=notreal@example.com")
        assert response.status_code == 200
        assert response.get_json()["exists"] is False


def test_save_genres_success(client):
    mock_token_info = {"email": "testuser@example.com"}
    mock_user = {"_id": ObjectId(), "email_address": "testuser@example.com"}

    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: mock_token_info)
    ), patch("api.user.read_user_by_email", return_value=mock_user), patch(
        "api.user.add_interest"
    ) as add_mock:

        headers = {"Authorization": "Bearer faketoken"}
        payload = {"genres": ["fantasy", "sci-fi"]}
        res = client.post("/user/save-genres", json=payload, headers=headers)

        assert res.status_code == 200
        assert res.get_json()["message"] == "Genres saved successfully"
        add_mock.assert_any_call(mock_user["_id"], "fantasy")
        add_mock.assert_any_call(mock_user["_id"], "sci-fi")


def test_get_user_profile_google_oauth_success(client):
    mock_token_info = {
        "email": "testuser@example.com",
        "given_name": "Test",
        "family_name": "User",
        "picture": "http://image.url/test.png",
    }

    mock_user = {
        "_id": ObjectId(),
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email_address": "testuser@example.com",
        "profile_image": "http://image.url/test.png",
        "created_at": "2023-01-01",
    }

    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: mock_token_info)
    ), patch("api.user.read_user_by_email", return_value=mock_user):

        headers = {"Authorization": "Bearer validtoken"}
        response = client.get("/user/profile", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Test User"
        assert data["email"] == "testuser@example.com"
        assert data["profile_picture"] == "http://image.url/test.png"


def test_get_user_profile_missing_email_from_token(client):
    with patch("api.user.requests.get", return_value=MagicMock(json=lambda: {})):
        headers = {"Authorization": "Bearer badtoken"}
        res = client.get("/user/profile", headers=headers)
        assert res.status_code == 200  # returns token_info JSON directly


def test_save_genres_invalid_format(client):
    mock_token_info = {"email": "t@example.com"}
    mock_user = {"_id": ObjectId(), "email_address": "t@example.com"}

    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: mock_token_info)
    ), patch("api.user.read_user_by_email", return_value=mock_user):

        headers = {"Authorization": "Bearer token"}
        res = client.post(
            "/user/save-genres", json={"genres": "notalist"}, headers=headers
        )
        assert res.status_code == 400
        assert "Genres must be a non-empty list" in res.get_json()["error"]


def test_get_user_profile_create_new_user(client):
    token_info = {
        "email": "newuser@example.com",
        "given_name": "New",
        "family_name": "User",
        "picture": "http://image.url/newuser.png",
    }

    new_user_id = str(ObjectId())
    new_user = {
        "_id": ObjectId(new_user_id),
        "first_name": "New",
        "last_name": "User",
        "username": "newuser",
        "email_address": "newuser@example.com",
        "profile_image": "http://image.url/newuser.png",
        "created_at": "2024-01-01",
    }

    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: token_info)
    ), patch(
        "api.user.read_user_by_email", side_effect=["User not found.", new_user]
    ), patch(
        "api.user.create_user", return_value=new_user_id
    ):

        headers = {"Authorization": "Bearer newusertoken"}
        res = client.get("/user/profile", headers=headers)

        assert res.status_code == 200
        data = res.get_json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["username"] == "newuser"
        assert data["profile_picture"] == "http://image.url/newuser.png"


def test_get_user_profile_missing_auth(client):
    response = client.get("/user/profile")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Missing or invalid Authorization header"


def test_save_genres_user_is_none(client):
    token_info = {"email": "nobody@example.com"}
    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: token_info)
    ), patch("api.user.read_user_by_email", return_value=None):

        headers = {"Authorization": "Bearer whatever"}
        response = client.post(
            "/user/save-genres", json={"genres": ["fiction"]}, headers=headers
        )
        assert response.status_code == 404
        assert response.get_json()["error"] == "User not found"


def test_save_genres_user_is_string(client):
    token_info = {"email": "nobody@example.com"}
    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: token_info)
    ), patch("api.user.read_user_by_email", return_value="User not found."):

        headers = {"Authorization": "Bearer something"}
        response = client.post(
            "/user/save-genres", json={"genres": ["nonfiction"]}, headers=headers
        )
        assert response.status_code == 404
        assert response.get_json()["error"] == "User not found"


def test_get_user_profile_user_still_string(client):
    token_info = {
        "email": "fail@example.com",
        "given_name": "Fail",
        "family_name": "Case",
        "picture": "http://image.url/fail.png",
    }

    with patch(
        "api.user.requests.get", return_value=MagicMock(json=lambda: token_info)
    ), patch(
        "api.user.read_user_by_email",
        side_effect=["User not found.", "User not found."],
    ), patch(
        "api.user.create_user", return_value=str(ObjectId())
    ):

        headers = {"Authorization": "Bearer failtoken"}
        res = client.get("/user/profile", headers=headers)
        assert res.status_code == 404
        assert "User not found." in res.get_json()["error"]


def test_edit_profile_user_lookup_returns_string(client):
    user_id = str(ObjectId())
    with patch("api.user.read_user_by_username", return_value="User not found"), patch(
        "api.user.update_user_settings", return_value="Profile updated successfully."
    ):

        response = client.post(
            f"/user/profile/{user_id}/edit-profile",
            json={
                "first_name": "Update",
                "last_name": "Me",
                "username": "existing_username",
                "profile_image": "img.jpg",
            },
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Profile updated successfully."


def test_get_user_by_id_exception(client):
    fake_id = str(ObjectId())

    with patch(
        "backend.models.users.read_user", side_effect=Exception("Unexpected failure")
    ):
        response = client.get(f"/user/profile/{fake_id}")
        assert response.status_code == 500
        assert "Unexpected failure" in response.get_json()["error"]


def test_edit_profile_username_exists_conflict(client):
    real_id = str(ObjectId())
    conflicting_user = {"_id": ObjectId()}

    with patch("api.user.read_user_by_username", return_value=conflicting_user):
        response = client.post(
            f"/user/profile/{real_id}/edit-profile", json={"username": "taken_user"}
        )
        assert response.status_code == 400
        assert response.get_json()["error"] == "Username already exists."


def test_edit_profile_same_user_id_as_existing(client):
    uid = str(ObjectId())
    existing_user = {"_id": ObjectId(uid)}  # same ID

    with patch("api.user.read_user_by_username", return_value=existing_user), patch(
        "api.user.update_user_settings", return_value="Profile updated successfully."
    ):

        response = client.post(
            f"/user/profile/{uid}/edit-profile", json={"username": "my_own_username"}
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Profile updated successfully."
