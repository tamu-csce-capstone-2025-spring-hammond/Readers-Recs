import uuid
from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.chat_messages import (
    create_chat_message,
    read_chat_message,
    read_chat_message_text,
    update_chat_message,
    delete_chat_message,
    get_all_chat_messages_for_book,
)
from main import app
from datetime import datetime, timedelta
from models.user_bookshelf import create_user_bookshelf


def test_chat_message_model_flow():
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="Chat",
        last_name="User",
        username=f"chatuser_{u}",
        email_address=f"chat_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )

    bid = create_book(
        title="Chat Book",
        author=["Author"],
        page_count=200,
        genre="Chat",
        tags=["chat"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="ChatPub",
        summary="Book for chat integration tests.",
        genre_tags=["test"],
    )

    try:
        # Create chat message
        mid = create_chat_message(bid, uid, "Hello, world!")
        assert isinstance(mid, str)

        # Read chat message
        msg = read_chat_message(mid)
        assert isinstance(msg, dict)
        assert msg["message_text"] == "Hello, world!"

        # Read message text
        text = read_chat_message_text(mid)
        assert text == "Hello, world!"

        # Update chat message
        updated = update_chat_message(mid, "Updated chat text")
        assert isinstance(updated, dict)
        assert updated["message_text"] == "Updated chat text"

        # Fetch all messages for book
        all_msgs = get_all_chat_messages_for_book(bid)
        assert isinstance(all_msgs, list)
        assert any(m["_id"] == mid or str(m["_id"]) == mid for m in all_msgs)

        # Delete message
        assert delete_chat_message(mid) == "Message deleted successfully."

    finally:
        delete_user(uid)
        delete_book(bid)


def test_chat_api_flow():
    client = app.test_client()
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="ChatAPI",
        last_name="User",
        username=f"chatapi_{u}",
        email_address=f"chatapi_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )

    bid = create_book(
        title="Chat API Book",
        author=["Author"],
        page_count=123,
        genre="Chat",
        tags=["chat"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Test Publisher",
        summary="Used for chat API testing.",
        genre_tags=["test"],
    )

    try:
        # Send chat message
        res = client.post(
            f"/api/chat/{bid}/send",
            json={"user_id": uid, "message_text": "Hello from test!"},
        )
        assert res.status_code == 201
        mid = res.json["message_id"]

        # Fetch chat messages for book
        res = client.get(f"/api/chat/{bid}/messages")
        assert res.status_code == 200
        assert any(msg["_id"] == mid or str(msg["_id"]) == mid for msg in res.json)

        # Missing user_id
        res = client.post(
            f"/api/chat/{bid}/send", json={"message_text": "Missing user"}
        )
        assert res.status_code == 400

        # Missing message_text
        res = client.post(f"/api/chat/{bid}/send", json={"user_id": uid})
        assert res.status_code == 400

    finally:
        delete_user(uid)
        delete_book(bid)


def test_chat_last_read_book_api_flow():
    client = app.test_client()
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="LastRead",
        last_name="User",
        username=f"lastread_{u}",
        email_address=f"lastread_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )

    bid1 = create_book(
        title="Older Book",
        author=["Author"],
        page_count=300,
        genre="History",
        tags=["read"],
        publication_date="2023-01-01",
        isbn=f"{u[:9]}1",
        isbn13=f"{u[:13]}1",
        cover_image="",
        language="en",
        publisher="History House",
        summary="This book was read earlier.",
        genre_tags=["history"],
    )

    bid2 = create_book(
        title="Newer Book",
        author=["Author"],
        page_count=350,
        genre="Sci-Fi",
        tags=["read"],
        publication_date="2024-01-01",
        isbn=f"{u[:9]}2",
        isbn13=f"{u[:13]}2",
        cover_image="",
        language="en",
        publisher="Future Press",
        summary="This book was read more recently.",
        genre_tags=["sci-fi"],
    )

    try:
        # Mark first book as read 10 days ago
        create_user_bookshelf(
            user_id=uid,
            book_id=bid1,
            status="read",
            date_finished=datetime.now() - timedelta(days=10),
            rating="mid",
        )

        # Mark second book as read yesterday
        create_user_bookshelf(
            user_id=uid,
            book_id=bid2,
            status="read",
            date_finished=datetime.now() - timedelta(days=1),
            rating="pos",
        )

        # Call the lastread endpoint
        res = client.get(f"/api/chat/user/{uid}/lastread")
        assert res.status_code == 200
        data = res.json
        assert data["title"] == "Newer Book"
        assert data["rating"] == "pos"
        assert "date_finished" in data

    finally:
        delete_user(uid)
        delete_book(bid1)
        delete_book(bid2)
