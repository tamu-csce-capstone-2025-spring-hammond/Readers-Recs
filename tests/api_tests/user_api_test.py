import pytest
import uuid
from bson import ObjectId
from main import app
from models.users import create_user, delete_user

app.testing = True

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_user():
    token = uuid.uuid4().hex
    email = f"{token}@test.com"
    user_id = create_user(
        first_name="Test",
        last_name="User",
        username=f"user_{token}",
        email_address=email,
        oauth={"access_token": token, "refresh_token": token},
        profile_image="",
        interests=[],
        demographics={"age": 22}
    )
    yield user_id, email
    delete_user(user_id)


# ---------------- GET /user/profile/<user_id> ---------------- #

def test_get_user_profile_valid(client, valid_user):
    user_id, _ = valid_user
    res = client.get(f"/user/profile/{user_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == user_id
    assert "name" in data
    assert "profile_picture" in data

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
    token = uuid.uuid4().hex
    email = f"{token}@example.com"
    user_id = create_user(
        first_name="", last_name="",
        username=f"blankuser_{token}",
        email_address=email,
        oauth={"access_token": token, "refresh_token": token},
        profile_image="",
        interests=[],
        demographics={}
    )
    try:
        res = client.get(f"/user/profile/{user_id}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["name"] == ""
        assert data["profile_picture"] == ""
    finally:
        delete_user(user_id)


# ---------------- POST /user/profile/<user_id>/edit-profile ---------------- #

def test_edit_profile_valid(client, valid_user):
    user_id, _ = valid_user
    response = client.post(
        f"/user/profile/{user_id}/edit-profile",
        json={
            "first_name": "Updated",
            "last_name": "Name",
            "username": f"updated_user_{user_id[:5]}",
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
    from api import user

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
    response = client.get("/user/check-email-exists?email=notreal@example.com")
    assert response.status_code == 200
    assert response.get_json()["exists"] is False
