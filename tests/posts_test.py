import pytest, uuid
from bson import ObjectId
from backend.models.posts import (
    create_post, read_post, read_post_field,
    update_post, delete_post, get_all_posts_for_book
)
from backend.models.users import create_user, delete_user
from backend.models.books import create_book, delete_book

@pytest.fixture
def user_and_book():
    # create a unique user
    unique = uuid.uuid4().hex
    uid = create_user(
        first_name="T", last_name="User",
        username=f"test_user_{unique}",
        email_address=f"{unique}@example.com",
        oauth={"access_token": unique, "refresh_token": unique},
        profile_image="", interests=[], demographics={}
    )
    # create a unique book
    bid = create_book(
        title="Test Book",
        author=["A"],
        page_count=1,
        genre="G",
        tags=["t"],
        publication_date="2025-01-01",
        isbn=unique[:9],
        isbn13=unique[:13],
        cover_image="",
        language="en",
        publisher="P",
        summary="S",
        genre_tags=["g"]
    )
    yield uid, bid
    delete_user(uid)
    delete_book(bid)

def test_crud_post_and_fields(user_and_book):
    uid, bid = user_and_book

    # CREATE
    pid = create_post(uid, bid, "My Title", "My Text", ["x","y"])
    assert isinstance(pid, str)

    # READ
    post = read_post(pid)
    assert str(post["_id"]) == pid
    assert post["title"] == "My Title"
    assert post["post_text"] == "My Text"
    assert post["tags"] == ["x", "y"]

    # READ SINGLE FIELD
    assert read_post_field(pid, "title") == "My Title"
    assert read_post_field(pid, "nonexistent") == "Post not found." or isinstance(read_post_field(pid, "nonexistent"), str)

    # UPDATE
    res = update_post(pid, title="New", post_text="NewText", tags="z")
    assert res == "Post updated successfully."
    updated = read_post(pid)
    assert updated["title"] == "New"
    assert updated["post_text"] == "NewText"
    assert updated["tags"] == ["z"]

    # LIST ALL FOR BOOK
    all_posts = get_all_posts_for_book(bid)
    assert isinstance(all_posts, list)
    assert any(str(p["_id"]) == pid for p in all_posts)

    # DELETE
    res = delete_post(pid)
    assert res == "Post deleted successfully."
    err = read_post(pid)
    assert err.startswith("Error:")

def test_invalid_ids_for_post():
    # completely bad IDs
    err = create_post("000000000000000000000000", "000000000000000000000000", "a", "b", [])
    assert err.startswith("Error:")
    assert err == "Error: Invalid user_id."

    # valid user, bad book
    unique = uuid.uuid4().hex
    uid = create_user(
        first_name="T", last_name="U",
        username=f"u2_{unique}", email_address=f"u2_{unique}@example.com",
        oauth={"access_token":unique, "refresh_token":unique},
        profile_image="", interests=[], demographics={}
    )
    try:
        assert create_post(uid, "000000000000000000000000", "a", "b", []) == "Error: Invalid book_id."
    finally:
        delete_user(uid)
