import numpy as np
from unittest.mock import patch, MagicMock
import recmodel
from pymongo import MongoClient
from bson import ObjectId
import json
import numpy as np
import re


@patch("recmodel.redis_client.get", return_value=json.dumps([0.1] * 384))
def test_retrieve_user_embedding_from_cache(mock_redis):
    embedding = recmodel.retrieve_user_embedding("some_user")
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == 384


@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
@patch(
    "recmodel.books_collection.find_one",
    return_value={"genre_tags": ["Fiction"], "embedding": [0.1] * 384},
)
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch("recmodel.update_genre_weights")
def test_process_user_rating_valid(mock_update, mock_weights, mock_find, mock_user):
    uid = str(ObjectId())
    recmodel.process_user_rating(uid, ObjectId(), "pos")
    mock_update.assert_called_once()


@patch("recmodel.retrieve_user_embedding", return_value=np.random.rand(384))
@patch("recmodel.retrieve_genre_weights", return_value={"Fantasy": 1})
@patch(
    "recmodel.books_collection.find",
    return_value=[
        {
            "_id": ObjectId(),
            "title": "A Fantasy Book",
            "author": ["J. Doe"],
            "genre_tags": ["Fantasy"],
            "embedding": list(np.random.rand(384)),
        }
    ],
)
@patch("recmodel.retrieve_user_bookshelf", return_value=[])
@patch("recmodel.get_unread_books", return_value=[])
def test_generate_recs_success(
    mock_unread, mock_shelf, mock_books, mock_weights, mock_embedding
):
    recs = recmodel.generate_recs("user123", top_n=3, count=1)
    assert isinstance(recs, list)
    assert 0 < len(recs) <= 3


@patch("recmodel.process_user_rating")
@patch("recmodel.retrieve_user_bookshelf")
def test_process_reading_history_calls_rating(mock_shelf, mock_process):
    uid = str(ObjectId())
    books = [
        {"book_id": ObjectId(), "rating": "pos"},
        {"book_id": ObjectId(), "rating": "neg"},
    ]
    mock_shelf.return_value = books

    recmodel.process_reading_history(uid)

    mock_shelf.assert_called_once_with(uid)
    assert mock_process.call_count == 2
    mock_process.assert_any_call(uid, books[0]["book_id"], "pos")
    mock_process.assert_any_call(uid, books[1]["book_id"], "neg")


@patch("recmodel.update_genre_weights")
@patch("recmodel.retrieve_genre_weights")
def test_update_genre_weights_only_increments_correctly(mock_retrieve, mock_update):
    uid = str(ObjectId())
    genres = ["Fantasy", "Sci-Fi", "Fantasy"]

    # Initial weights
    mock_retrieve.return_value = {"Fantasy": 1, "Romance": 2}

    recmodel.update_genre_weights_only(uid, genres)

    expected = {
        "Fantasy": 3,  # 1 + 2
        "Romance": 2,
        "Sci-Fi": 1,  # new genre added
    }

    mock_retrieve.assert_called_once_with(uid)
    mock_update.assert_called_once_with(uid, expected)


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_embedding")
@patch("recmodel.update_genre_weights")
@patch("recmodel.retrieve_genre_weights")
@patch("recmodel.read_user")
@patch("recmodel.books_collection.find_one")
@patch("recmodel.get_unread_books")
def test_process_wishlist_all_steps_success(
    mock_unread,
    mock_find,
    mock_user,
    mock_gweights,
    mock_update_gweights,
    mock_user_embed,
    mock_update_embed,
):
    uid = str(ObjectId())
    bid = ObjectId()

    # Mock unread shelf
    mock_unread.return_value = [{"book_id": bid}]

    # Mock book from collection
    mock_find.return_value = {
        "_id": bid,
        "genre_tags": ["Fantasy", "Mystery"],
        "embedding": [0.4] * 384,
    }

    # Mock user retrieval
    mock_user.return_value = {"_id": uid}

    # Mock genre weights
    mock_gweights.return_value = {"Fantasy": 1.0}

    # Mock embeddings
    mock_user_embed.return_value = np.array([0.2] * 384)

    recmodel.process_wishlist(uid)

    mock_unread.assert_called_once_with(uid)
    mock_find.assert_called_once_with({"_id": bid})
    mock_user.assert_called_once_with(uid)

    # Final genre weight after 0.5 increments
    expected_weights = {"Fantasy": 1.5, "Mystery": 0.5}
    mock_update_gweights.assert_called_with(uid, expected_weights)

    # Embedding should be averaged
    expected_embedding = ((np.array([0.2] * 384) + np.array([0.4] * 384)) / 2).tolist()
    mock_update_embed.assert_called_with(uid, expected_embedding)


@patch("recmodel.books_collection.update_one")
@patch("recmodel.model.encode")
def test_update_book_embeddings_missing_embedding(mock_encode, mock_update):
    book_id = ObjectId()
    books = [{"_id": book_id, "title": "Book A", "summary": "This is a test summary."}]

    # Mock the model returning a single 384-dim embedding
    mock_encode.return_value = np.array([[0.1] * 384])
    mock_update.return_value.modified_count = 1

    recmodel.update_book_embeddings(books)

    mock_encode.assert_called_once_with(
        ["This is a test summary."], convert_to_numpy=True
    )
    mock_update.assert_called_once_with(
        {"_id": book_id}, {"$set": {"embedding": [0.1] * 384}}
    )


def test_are_titles_similar_identical():
    assert recmodel.are_titles_similar("The Great Gatsby", "The Great Gatsby") is True


def test_are_titles_similar_above_threshold():
    assert recmodel.are_titles_similar("AI for Beginners", "A.I. for Beginners") is True


def test_are_titles_similar_below_threshold():
    assert recmodel.are_titles_similar("War and Peace", "Cooking Recipes") is False


def test_are_titles_similar_custom_threshold():
    assert (
        recmodel.are_titles_similar("Deep Learning", "Deep Learn", threshold=90)
        is False
    )


@patch("recmodel.are_titles_similar", return_value=False)
def test_is_duplicate_author_overlap(mock_titles):
    book1 = {"title": "Book One", "author": ["Alice Smith"]}
    book2 = {"title": "Completely Different", "author": ["alice smith"]}

    assert recmodel.is_duplicate(book1, book2) is True
    mock_titles.assert_not_called()


@patch("recmodel.are_titles_similar", return_value=True)
def test_is_duplicate_title_similarity(mock_titles):
    book1 = {"title": "The Adventures of AI", "author": ["Someone"]}
    book2 = {"title": "Adventures of Artificial Intelligence", "author": ["Nobody"]}

    assert recmodel.is_duplicate(book1, book2) is True
    mock_titles.assert_called_once()


@patch("recmodel.are_titles_similar", return_value=False)
def test_is_not_duplicate(mock_titles):
    book1 = {"title": "Book A", "author": ["Author A"]}
    book2 = {"title": "Book B", "author": ["Author B"]}

    assert recmodel.is_duplicate(book1, book2) is False


@patch("recmodel.read_user")
@patch("recmodel.books_collection.find_one")
def test_process_user_rating_no_rating(mock_find, mock_user):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, None)
    mock_user.assert_not_called()
    mock_find.assert_not_called()


@patch("recmodel.read_user")
@patch("recmodel.books_collection.find_one")
def test_process_user_rating_invalid_rating(mock_find, mock_user):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, "excellent")
    mock_user.assert_not_called()
    mock_find.assert_not_called()


@patch("recmodel.read_user", return_value=None)
@patch("recmodel.books_collection.find_one")
def test_process_user_rating_user_not_found(mock_find, mock_user):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, "mid")
    # Expect book still fetched but no downstream logic executed
    mock_find.assert_called_once_with({"_id": bid})


@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
@patch("recmodel.books_collection.find_one", return_value=None)
def test_process_user_rating_book_not_found(mock_find, mock_user):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, "neg")
    mock_find.assert_called_once_with({"_id": bid})


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=np.array([0.1] * 384))
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch(
    "recmodel.books_collection.find_one",
    return_value={"genre_tags": ["Drama"], "embedding": None},
)
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_user_rating_missing_book_embedding(
    mock_user, mock_find, mock_weights, mock_embedding, mock_update_embed
):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, "pos")

    # Confirm that update_user_embedding is not called due to missing embedding
    mock_update_embed.assert_not_called()


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=np.array([0.1] * 384))
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch(
    "recmodel.books_collection.find_one",
    return_value={"genre_tags": ["Sci-Fi"], "embedding": []},
)
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_user_rating_empty_book_embedding(
    mock_user, mock_find, mock_gweights, mock_user_embed, mock_update_embed
):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, "pos")

    # Embedding is empty, so update_user_embedding should not be called
    mock_update_embed.assert_not_called()


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=None)
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch("recmodel.books_collection.find_one")
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_user_rating_triggers_empty_user_embedding(
    mock_user, mock_find, mock_weights, mock_user_embed, mock_update_embed
):
    uid = str(ObjectId())
    bid = ObjectId()

    mock_find.return_value = {"genre_tags": ["Fantasy"], "embedding": [0.1] * 384}

    recmodel.process_user_rating(uid, bid, "pos")

    # Verify update_user_embedding was called with correct parameters
    args, _ = mock_update_embed.call_args
    assert args[0] == uid
    assert isinstance(args[1], list)
    assert all(round(v, 2) == 0.05 for v in args[1])  # (0 + 0.1)/2


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=np.array([0.1] * 384))
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch(
    "recmodel.books_collection.find_one", return_value={"genre_tags": ["Horror"]}
)  # missing "embedding"
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_user_rating_missing_embedding(
    mock_user, mock_find, mock_weights, mock_user_embed, mock_update_embed
):
    uid = str(ObjectId())
    bid = ObjectId()

    recmodel.process_user_rating(uid, bid, "pos")

    mock_update_embed.assert_not_called()


def test_update_book_embeddings_non_iterable():
    # Should handle gracefully and print an error
    result = recmodel.update_book_embeddings(None)
    assert result == []


@patch("recmodel.generate_recs", return_value=[{"title": "Test Book"}])
@patch("recmodel.process_wishlist")
@patch("recmodel.process_reading_history")
@patch("recmodel.update_embedding")
@patch("recmodel.update_genre_weights")
def test_recommend_books_success(
    mock_weights, mock_embed, mock_reading, mock_wishlist, mock_recs
):
    user_id = str(ObjectId())

    result = recmodel.recommend_books(user_id, count=1)

    mock_weights.assert_called_once_with(user_id, {})

    # Manually extract and validate array values
    embed_args, _ = mock_embed.call_args
    assert embed_args[0] == user_id
    assert isinstance(embed_args[1], np.ndarray)
    assert embed_args[1].shape == (384,)
    assert np.all(embed_args[1] == 0.0)

    assert result == [{"title": "Test Book"}]


@patch("recmodel.update_genre_weights_only")
def test_onboarding_recommendations_success(mock_update):
    user_id = "680975b2f2f539aaba308487"
    interests = ["Fiction", "Sci-Fi"]

    result = recmodel.onboarding_recommendations(user_id, interests)

    mock_update.assert_called_once_with(user_id, interests)
    assert result is True


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=np.array([0.1] * 384))
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch("recmodel.books_collection.find_one", return_value=None)
@patch("recmodel.get_unread_books", return_value=[{"book_id": ObjectId()}])
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_wishlist_book_not_found(
    mock_read_user,
    mock_unread,
    mock_find_one,
    mock_weights,
    mock_user_embed,
    mock_update_embed,
):
    recmodel.process_wishlist(str(ObjectId()))
    mock_update_embed.assert_not_called()


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding")
@patch("recmodel.retrieve_genre_weights")
@patch(
    "recmodel.books_collection.find_one",
    return_value={"genre_tags": ["Drama"], "embedding": [0.1] * 384},
)
@patch("recmodel.get_unread_books", return_value=[{"book_id": ObjectId()}])
@patch("recmodel.read_user", return_value=None)
def test_process_wishlist_user_not_found(
    mock_read_user, *_  # Other mocks unused if user is None
):
    recmodel.process_wishlist(str(ObjectId()))
    mock_read_user.assert_called()


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=np.array([0.1] * 384))
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch(
    "recmodel.books_collection.find_one",
    return_value={"genre_tags": ["Fantasy"], "embedding": []},
)
@patch("recmodel.get_unread_books", return_value=[{"book_id": ObjectId()}])
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_wishlist_book_empty_embedding(*_):
    recmodel.process_wishlist(str(ObjectId()))


@patch("recmodel.update_user_embedding")
@patch("recmodel.retrieve_user_embedding", return_value=None)
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch(
    "recmodel.books_collection.find_one",
    return_value={"genre_tags": ["Action"], "embedding": [0.2] * 384},
)
@patch("recmodel.get_unread_books", return_value=[{"book_id": ObjectId()}])
@patch("recmodel.read_user", return_value={"_id": str(ObjectId())})
def test_process_wishlist_empty_user_embedding(
    mock_read_user,
    mock_unread,
    mock_find,
    mock_weights,
    mock_user_embed,
    mock_update_embed,
):
    recmodel.process_wishlist(str(ObjectId()))
    args, _ = mock_update_embed.call_args
    assert isinstance(args[1], list)
    assert np.allclose(args[1], np.array([0.1] * 384))


@patch("recmodel.retrieve_user_embedding", return_value=None)
@patch(
    "recmodel.books_collection.find",
    return_value=[
        {
            "_id": ObjectId(),
            "title": "Book A",
            "author": ["Author A"],
            "genre_tags": ["Fiction"],
            "embedding": [0.1] * 384,
        }
    ],
)
@patch("recmodel.retrieve_genre_weights", return_value={})
@patch("recmodel.retrieve_user_bookshelf", return_value=[])
@patch("recmodel.get_unread_books", return_value=[])
def test_generate_recs_user_embedding_none(
    mock_unread, mock_read, mock_weights, mock_books, mock_user_embed
):
    result = recmodel.generate_recs(user_id="user123", count=5)
    assert result == []  # Expecting early return due to missing user_embedding


@patch("recmodel.retrieve_embedding", return_value=np.array([0.1] * 384))
@patch(
    "recmodel.books_collection.find",
    return_value=[
        {"_id": ObjectId(), "title": "Book A", "embedding": None},  # invalid embedding
        {"_id": ObjectId(), "title": "Book B", "embedding": []},  # empty embedding
    ],
)
@patch("recmodel.retrieve_user_bookshelf", return_value=[])
@patch("recmodel.get_unread_books", return_value=[])
def test_generate_recs_empty_book_embeddings(
    mock_unread, mock_shelf, mock_books, mock_embed
):
    result = recmodel.generate_recs("user_id", count=5)
    assert result == []


@patch("recmodel.retrieve_embedding", return_value=np.zeros(384))
@patch("recmodel.retrieve_genre_weights", return_value={"fantasy": 2, "mystery": 1})
@patch(
    "recmodel.books_collection.find",
    return_value=[
        {
            "_id": ObjectId(),
            "title": "Mystery Book",
            "author": ["Author A"],
            "genre_tags": ["Mystery"],
            "embedding": [0.1] * 384,
        },
        {
            "_id": ObjectId(),
            "title": "Fantasy Book",
            "author": ["Author B"],
            "genre_tags": ["Fantasy"],
            "embedding": [0.1] * 384,
        },
    ],
)
@patch("recmodel.retrieve_user_bookshelf", return_value=[])
@patch("recmodel.get_unread_books", return_value=[])
def test_generate_recs_genre_only_fallback(*_):
    recs = recmodel.generate_recs("user123", top_n=2, count=1)
    assert len(recs) >= 1
    titles = [r["title"] for r in recs]
    assert "Fantasy Book" in titles or "Mystery Book" in titles


@patch("recmodel.redis_client.get", return_value=None)  # Simulate empty cache
@patch("recmodel.redis_client.set")
@patch(
    "recmodel.retrieve_embedding", return_value=[0.1] * 384
)  # Return a list instead of ndarray
def test_retrieve_user_embedding_non_ndarray(mock_retrieve, mock_set, mock_redis_get):
    uid = "mock_user"

    result = recmodel.retrieve_user_embedding(uid)

    # Verify the result is valid
    assert isinstance(result, list) or isinstance(result, np.ndarray)
    mock_set.assert_called_once()

    # Extract args and check the serialized value
    args, kwargs = mock_set.call_args
    assert args[0] == f"user_embedding:{uid}"
    serialized_embedding = args[1]
    assert isinstance(json.loads(serialized_embedding), list)
    assert kwargs["ex"] == 3600


@patch("recmodel.retrieve_embedding", return_value=np.array([0.1] * 384))
@patch("recmodel.retrieve_genre_weights", return_value={"fiction": 1})
@patch("recmodel.books_collection.find")
@patch("recmodel.retrieve_user_bookshelf", return_value=[])
@patch("recmodel.get_unread_books", return_value=[])
def test_generate_recs_triggers_adjust_author(
    mock_unread, mock_shelf, mock_find, mock_weights, mock_embed
):
    user_id = "user_id"

    base_book = {
        "genre_tags": ["Fiction"],
        "embedding": [0.1] * 384,
    }

    books = [
        {
            **base_book,
            "_id": "id1",
            "title": "Book A",
            "author": ["John Smith"],
        },  # best
        {**base_book, "_id": "id2", "title": "Book B", "author": ["Jane Doe"]},  # best
        {
            **base_book,
            "_id": "id3",
            "title": "Book C",
            "author": ["john smith"],
        },  # duplicate
        {**base_book, "_id": "id4", "title": "Book D", "author": ["Alice"]},
    ]

    mock_find.return_value = books

    # count=2 will include best_books[0:2] and leave id3 & id4 for remaining_books
    recs = recmodel.generate_recs(user_id, count=2)

    # Confirm duplicate was filtered, only 3 books returned (id3 skipped)
    titles = [book["title"] for book in recs]
    assert "Book A" in titles
    assert "Book B" in titles
    assert "Book D" not in titles  # filtered due to similar title
    assert "Book C" not in titles  # filtered due to duplicate author
