import uuid
from flask.testing import FlaskClient
from main import app
from models.users import delete_user
from database import collections
from unittest.mock import patch
from bson import ObjectId


@patch("requests.get")
def test_oauth_user_recommendation_flow(mock_get):
    client: FlaskClient = app.test_client()
    unique = uuid.uuid4().hex
    email = f"rec_test_{unique}@example.com"
    token = f"token_{unique}"
    user_id = None
    book_id = None

    fake_token_info = {
        "email": email,
        "given_name": "Rec",
        "family_name": "Tester",
        "picture": "https://example.com/avatar.jpg",
    }

    mock_get.return_value.json.return_value = fake_token_info
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Step 1: Simulate OAuth login, user creation
        res = client.get("/user/profile", headers=headers)
        assert res.status_code == 200
        user_id = res.json["id"]

        # Step 2: Save genres
        genres = ["fantasy", "science fiction"]
        res = client.post("/user/save-genres", headers=headers, json={"genres": genres})
        assert res.status_code == 200
        assert res.json["message"] == "Genres saved successfully"

        # Step 3: Onboarding recommendations
        res = client.post(
            "/recs/api/user/onboarding/recommendations",
            headers=headers,
            json={"genres": genres},
        )
        assert res.status_code == 200

        # Step 3b: Now fetch actual recommendations
        res = client.get(f"/recs/api/user/{user_id}/recommendations")
        assert res.status_code == 200
        recs = res.json["recommendations"]
        assert isinstance(recs, list) and len(recs) > 0
        book_id = recs[0]["_id"]

        # Step 4: Add to bookshelf
        res = client.post(
            f"/shelf/api/user/{user_id}/bookshelf",
            json={"book_id": book_id, "status": "to-read", "rating": "mid"},
        )
        assert res.status_code == 201

        # Step 5: Update status
        res = client.put(
            f"/shelf/api/user/{user_id}/bookshelf/{book_id}/status",
            json={"status": "currently-reading"},
        )
        assert res.status_code == 200

        # Step 6: Final recs
        res = client.get(f"/recs/api/user/{user_id}/recommendations")
        assert res.status_code == 200
        assert len(res.json["recommendations"]) > 0

    finally:
        if user_id:
            delete_user(user_id)
            assert collections["Users"].find_one({"_id": ObjectId(user_id)}) is None
