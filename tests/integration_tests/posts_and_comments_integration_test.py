from models.users import create_user, delete_user
from models.books import create_book, delete_book
from models.posts import (
    create_post,
    read_post,
    update_post,
    delete_post,
    get_all_posts_for_book,
)
from models.comments import (
    create_initial_comment,
    read_comment,
    reply_to_comment,
    update_comment,
    delete_comment,
    get_all_comments_for_post,
)
import uuid
from main import app


def test_post_model_flow():
    u = uuid.uuid4().hex
    uid = create_user(
        first_name="Post",
        last_name="User",
        username=f"postuser_{u}",
        email_address=f"post_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="Post Book",
        author=["Author"],
        page_count=100,
        genre="Discussion",
        tags=["post"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["discussion"],
    )

    try:
        pid = create_post(uid, bid, "Test Title", "This is a post body", ["tag1"])
        assert isinstance(pid, str)

        post = read_post(pid)
        assert isinstance(post, dict), f"read_post failed: {post}"
        assert post["title"] == "Test Title"

        assert (
            update_post(pid, title="Updated", post_text="Updated Text")
            == "Post updated successfully."
        )
        post = read_post(pid)
        assert post["title"] == "Updated"

        all_posts = get_all_posts_for_book(bid)
        assert any(str(p["_id"]) == pid for p in all_posts)

        assert delete_post(pid) == "Post deleted successfully."
        assert read_post(pid).startswith("Error:")

    finally:
        delete_user(uid)
        delete_book(bid)


def test_comment_model_flow():
    u = uuid.uuid4().hex
    uid = create_user(
        first_name="Comment",
        last_name="User",
        username=f"commentuser_{u}",
        email_address=f"comment_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="Comment Book",
        author=["Author"],
        page_count=100,
        genre="Discussion",
        tags=["comment"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["discussion"],
    )
    pid = create_post(uid, bid, "Post Title", "Post content", ["tag"])

    try:
        cid = create_initial_comment(pid, uid, "Initial comment")
        assert isinstance(cid, str)

        comment = read_comment(cid)
        assert comment["comment_text"] == "Initial comment"

        reply_id = reply_to_comment(pid, uid, "Reply here", parent_comment_id=cid)
        assert isinstance(reply_id, str)

        all_comments = get_all_comments_for_post(pid)
        parent = next((c for c in all_comments if c["_id"] == cid), None)
        assert parent and any(r["_id"] == reply_id for r in parent.get("replies", []))

        assert update_comment(cid, "Updated comment") == "Comment updated successfully."
        updated = read_comment(cid)
        assert updated["comment_text"] == "Updated comment"

        assert delete_comment(reply_id) == "Comment deleted successfully."
        assert delete_comment(cid) == "Comment deleted successfully."

    finally:
        delete_post(pid)
        delete_user(uid)
        delete_book(bid)


def test_post_api_flow():
    client = app.test_client()
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="PostAPI",
        last_name="User",
        username=f"postapi_{u}",
        email_address=f"postapi_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="API Post Book",
        author=["Author"],
        page_count=100,
        genre="Test",
        tags=["post"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Publisher",
        summary="Summary",
        genre_tags=["api"],
    )

    try:
        # Create Post
        res = client.post(
            f"/api/books/{bid}/posts",
            json={
                "user_id": uid,
                "title": "API Post",
                "post_text": "Hello world",
                "tags": ["flask", "test"],
            },
        )
        assert res.status_code == 201
        pid = res.json["post_id"]

        # Get all posts for book
        res = client.get(f"/api/books/{bid}/posts")
        assert res.status_code == 200
        assert any(post["_id"] == pid for post in res.json)

    finally:
        delete_user(uid)
        delete_book(bid)


def test_comment_api_flow():
    client = app.test_client()
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="CommentAPI",
        last_name="User",
        username=f"commentapi_{u}",
        email_address=f"commentapi_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )
    bid = create_book(
        title="Comment API Book",
        author=["Author"],
        page_count=100,
        genre="Test",
        tags=["comment"],
        publication_date="2025-01-01",
        isbn=u[:9],
        isbn13=u[:13],
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["api"],
    )
    pid = create_post(uid, bid, "Post for Comments", "Text", ["tag"])

    try:
        # Create comment
        res = client.post(
            f"/api/posts/{pid}/comments",
            json={"user_id": uid, "comment_text": "First comment"},
        )
        assert res.status_code == 201
        cid = res.json["comment_id"]

        # Reply to comment
        res = client.post(
            f"/api/posts/{pid}/comments",
            json={
                "user_id": uid,
                "comment_text": "This is a reply",
                "parent_comment_id": cid,
            },
        )
        assert res.status_code == 201
        res.json["comment_id"]

        # Get all comments for post
        res = client.get(f"/api/posts/{pid}/comments")
        assert res.status_code == 200
        assert any(c["_id"] == cid for c in res.json)

    finally:
        delete_post(pid)
        delete_user(uid)
        delete_book(bid)
