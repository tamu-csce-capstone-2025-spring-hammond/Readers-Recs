import uuid
from flask.testing import FlaskClient
from main import app
from models.users import delete_user
from database import collections
from unittest.mock import patch
from bson import ObjectId


@patch("requests.get")
def test_full_user_lifecycle_with_ratings(mock_get):
    client: FlaskClient = app.test_client()
    unique = uuid.uuid4().hex
    email = f"user_{unique}@example.com"
    token = f"token_{unique}"
    user_id = post_id = comment_id = chat_msg_id = None
    book_ids = []

    fake_token_info = {
        "email": email,
        "given_name": "Full",
        "family_name": "Test",
        "picture": "https://example.com/avatar.jpg",
    }

    mock_get.return_value.json.return_value = fake_token_info
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Step 1: OAuth login → user creation
        res = client.get("/user/profile", headers=headers)
        assert res.status_code == 200
        user_id = res.json["id"]

        # Step 2: Select interests
        genres = ["fantasy", "science fiction"]
        res = client.post("/user/save-genres", headers=headers, json={"genres": genres})
        assert res.status_code == 200

        # Step 3: Get recommendations
        res = client.get(f"/recs/api/user/{user_id}/recommendations")
        assert res.status_code == 200
        recommendations = res.json["recommendations"]
        assert len(recommendations) >= 3
        book_ids = [rec["_id"] for rec in recommendations[:3]]

        for i, book_id in enumerate(book_ids):
            # Step 4: Add book to bookshelf
            res = client.post(
                f"/shelf/api/user/{user_id}/bookshelf",
                json={"book_id": book_id, "status": "to-read", "rating": "mid"},
            )
            assert res.status_code == 201

            # Step 5: Update book status to 'currently-reading'
            res = client.put(
                f"/shelf/api/user/{user_id}/bookshelf/{book_id}/status",
                json={"status": "currently-reading"},
            )
            assert res.status_code == 200

            # Step 6: Update book status to 'read'
            res = client.put(
                f"/shelf/api/user/{user_id}/bookshelf/{book_id}/status",
                json={"status": "read"},
            )
            assert res.status_code == 200

            # Step 7: Rate the book
            rating = ["pos", "mid", "neg"][i % 3]
            res = client.put(
                f"/shelf/api/user/{user_id}/bookshelf/{book_id}/rating",
                json={"rating": rating},
            )
            assert res.status_code == 200

        # Step 8: Create a post for the first book
        res = client.post(
            f"/api/books/{book_ids[0]}/posts",
            json={
                "user_id": user_id,
                "title": "Favorite Book",
                "post_text": "This was a game changer!",
                "tags": ["favorite"],
            },
        )
        assert res.status_code == 201
        post_id = res.json["post_id"]

        # Step 9: Add a comment
        res = client.post(
            f"/api/posts/{post_id}/comments",
            json={"user_id": user_id, "comment_text": "Loved this discussion!"},
        )
        assert res.status_code == 201
        comment_id = res.json["comment_id"]

        # Step 10: Send a group chat message for second book
        res = client.post(
            f"/api/chat/{book_ids[1]}/send",
            json={
                "user_id": user_id,
                "message_text": "Anyone else reading this right now?",
            },
        )
        assert res.status_code == 201
        chat_msg_id = res.json["message_id"]

        # Step 11: Final recommendation refresh
        res = client.get(f"/recs/api/user/{user_id}/recommendations")
        assert res.status_code == 200
        assert len(res.json["recommendations"]) > 0

    finally:
        if user_id:
            delete_user(user_id)
            assert collections["Users"].find_one({"_id": ObjectId(user_id)}) is None
