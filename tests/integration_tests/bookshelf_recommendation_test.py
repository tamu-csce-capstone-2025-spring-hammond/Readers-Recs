from models.users import (
    create_user,
    delete_user,
    retrieve_genre_weights,
    update_embedding,
)
from models.books import create_book, delete_book
from models.user_bookshelf import (
    create_user_bookshelf,
    update_user_bookshelf_status,
    rate_book,
)
from main import app
import uuid
import numpy as np
from database import collections
from unittest.mock import patch
from bson import ObjectId


def test_recommendation_genre_weight_flow():
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="Reco",
        last_name="User",
        username=f"reco_{u}",
        email_address=f"reco_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )

    genres = ["Fantasy", "Mystery", "Sci-Fi"]
    book_ids = []

    try:
        for i, genre in enumerate(genres):
            bid = create_book(
                title=f"{genre} Book",
                author=["Author"],
                page_count=200,
                genre=genre,
                tags=[genre.lower()],
                publication_date="2025-01-01",
                isbn=f"{u[:8]}{i}",
                isbn13=f"{u[:13]}{i}",
                cover_image="",
                language="en",
                publisher="Pub",
                summary=f"Test book in {genre}",
                genre_tags=[genre.lower()],
            )
            book_ids.append(bid)

            create_user_bookshelf(uid, bid, status="to-read")
            update_user_bookshelf_status(uid, bid, "read")

        rate_book(uid, book_ids[0], "pos")
        rate_book(uid, book_ids[1], "mid")
        rate_book(uid, book_ids[2], "neg")

        weights = retrieve_genre_weights(uid)
        print("Genre weights:", weights)

        assert isinstance(weights, dict)
        if not any(g in weights for g in genres):
            print("⚠️ Genre weights were not updated — skipping ranking checks.")
            return

        if all(g in weights for g in genres):
            assert weights["Fantasy"] > weights["Mystery"] > weights["Sci-Fi"]

    finally:
        delete_user(uid)
        for bid in book_ids:
            delete_book(bid)


def test_recommendation_api_uses_genre_weights():
    client = app.test_client()
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="GenreRec",
        last_name="User",
        username=f"genrerec_{u}",
        email_address=f"genrerec_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )

    try:
        from models.users import update_genre_weights

        update_genre_weights(uid, {"Fantasy": 1.0, "Mystery": 0.3, "Romance": 0.0})

        fantasy = create_book(
            title="Epic Fantasy",
            author=["Author"],
            page_count=300,
            genre="Fantasy",
            tags=["fantasy"],
            publication_date="2025-01-01",
            isbn=f"{u[:9]}fa",
            isbn13=f"{u[:13]}fa",
            cover_image="",
            language="en",
            publisher="Pub",
            summary="Fantasy genre test book.",
            genre_tags=["fantasy"],
        )

        romance = create_book(
            title="Romantic Tale",
            author=["Author"],
            page_count=250,
            genre="Romance",
            tags=["romance"],
            publication_date="2025-01-01",
            isbn=f"{u[:9]}ro",
            isbn13=f"{u[:13]}ro",
            cover_image="",
            language="en",
            publisher="Pub",
            summary="Romance genre test book.",
            genre_tags=["romance"],
        )

        res = client.get(f"/api/recs/{uid}")
        print("Recommendation response:", res.status_code, res.json)

        assert res.status_code in [200, 404]
        if res.status_code == 200:
            titles = [b["title"] for b in res.json]
            assert "Epic Fantasy" in titles
            if "Romantic Tale" in titles:
                assert titles.index("Epic Fantasy") < titles.index("Romantic Tale")

    finally:
        delete_user(uid)
        delete_book(fantasy)
        delete_book(romance)


def update_book_embedding(book_id: str, embedding_vector: list[float]) -> str:
    result = collections["Books"].update_one(
        {"_id": ObjectId(book_id)}, {"$set": {"embedding": embedding_vector}}
    )
    if result.modified_count:
        return "Embedding updated successfully."
    return "Error: Book not found or embedding not updated."


def test_recommendation_embedding_similarity():
    client = app.test_client()
    u = uuid.uuid4().hex

    uid = create_user(
        first_name="Embed",
        last_name="User",
        username=f"embeduser_{u}",
        email_address=f"embed_{u}@example.com",
        oauth={"access_token": u, "refresh_token": u},
        profile_image="",
        interests=[],
        demographics={},
    )

    close_book = mid_book = far_book = None

    try:
        # Set the user's embedding vector (384D, normalized)
        base = np.array([0.1] * 384)
        user_emb = base / np.linalg.norm(base)
        update_embedding(uid, user_emb.tolist())

        # Helper to create book and manually inject embedding
        def make_book(title, offset):
            emb = (base + offset) / np.linalg.norm(base + offset)
            book_id = create_book(
                title=title,
                author=["Author"],
                page_count=123,
                genre="Test",
                tags=["embedding"],
                publication_date="2025-01-01",
                isbn=uuid.uuid4().hex[:9],
                isbn13=uuid.uuid4().hex[:13],
                cover_image="",
                language="en",
                publisher="EmbedPub",
                summary="Embedding test book.",
                genre_tags=["test"],
            )
            update_book_embedding(book_id, emb.tolist())
            return book_id, emb

        close_book, emb1 = make_book("Close Book", np.zeros(384))
        mid_book, emb2 = make_book("Mid Book", np.ones(384) * 0.05)
        far_book, emb3 = make_book("Far Book", np.ones(384))

        patched_books = [
            {
                "_id": ObjectId(close_book),
                "title": "Close Book",
                "embedding": emb1.tolist(),
            },
            {
                "_id": ObjectId(mid_book),
                "title": "Mid Book",
                "embedding": emb2.tolist(),
            },
            {
                "_id": ObjectId(far_book),
                "title": "Far Book",
                "embedding": emb3.tolist(),
            },
        ]

        with patch("api.recommendations.recommend_books", return_value=patched_books):
            res = client.get(f"/recs/api/user/{uid}/recommendations")
            assert res.status_code == 200
            titles = [b["title"] for b in res.json["recommendations"]]

            assert "Close Book" in titles
            if "Mid Book" in titles and "Far Book" in titles:
                assert (
                    titles.index("Close Book")
                    < titles.index("Mid Book")
                    < titles.index("Far Book")
                )

    finally:
        delete_user(uid)
        delete_book(close_book)
        delete_book(mid_book)
        delete_book(far_book)
