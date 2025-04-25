import uuid
from flask.testing import FlaskClient
from main import app
from models.users import delete_user
from database import collections
from unittest.mock import patch
from bson import ObjectId


def test_oauth_user_create_update_delete():
    client: FlaskClient = app.test_client()
    unique = uuid.uuid4().hex
    email = f"sys_test_{unique}@example.com"
    fake_token = f"token_{unique}"
    user_id = None

    # Fake Google token info and user profile
    fake_token_info = {
        "email": email,
        "given_name": "System",
        "family_name": "Tester",
        "picture": "https://example.com/pfp.jpg",
    }

    try:
        # Step 1: Simulate OAuth-based user creation
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_token_info
            headers = {"Authorization": f"Bearer {fake_token}"}
            res = client.get("/user/profile", headers=headers)
            assert res.status_code == 200
            user_id = res.json["id"]

        assert user_id and len(user_id) == 24
        user_doc = collections["Users"].find_one({"_id": ObjectId(user_id)})
        assert user_doc and user_doc["email_address"] == email

        # Step 2: Update user via edit-profile
        res = client.post(
            f"/user/profile/{user_id}/edit-profile",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "username": f"updated_{unique}",
                "profile_image": "https://example.com/updated.jpg",
            },
        )
        assert res.status_code == 200
        assert res.json["message"] == "Profile updated successfully."

        updated = collections["Users"].find_one({"_id": ObjectId(user_id)})
        assert updated["first_name"] == "Updated"
        assert updated["username"] == f"updated_{unique}"

    finally:
        if user_id:
            delete_user(user_id)
            assert collections["Users"].find_one({"_id": ObjectId(user_id)}) is None
