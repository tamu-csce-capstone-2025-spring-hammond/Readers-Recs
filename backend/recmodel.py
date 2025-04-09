import collections
import random
from load_books import BookCollection
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from models.books import books_collection
import redis
import json
import re
from fuzzywuzzy import fuzz


from models.users import (
    read_user,
    retrieve_embedding,
    retrieve_genre_weights,
    update_embedding,
    update_genre_weights,
)
from models.user_bookshelf import get_unread_books, retrieve_user_bookshelf

# Initialize the book collection on startup
book_collection = BookCollection()

# load_dotenv(override=True)
# uri = os.getenv("MONGO_URI")
# if not uri:
#     raise ValueError("MONGO_URI is not set")

# # Initialize MongoDB and Redis
# client = MongoClient(uri, server_api=ServerApi("1"))
# db = client["book_recommendation"]
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# Load SentenceTransformer model once
#model = SentenceTransformer("all-MiniLM-L6-v2")

model_name = "all-MiniLM-L6-v2"
try:
    model = SentenceTransformer(model_name)
    print("Model loaded successfully with SentenceTransformer.")
except Exception as e:
    print(f"Error loading model: {e}")


def process_reading_history(user_id):
    books_read = retrieve_user_bookshelf(user_id)
    # print("Books read:", books_read)

    for book in books_read:
        book_id = book["book_id"]
        rating = book["rating"]
        process_user_rating(user_id, book_id, rating)

def update_genre_weights_only(user_id, interested_genres):
    genre_weights = dict()
    for genre in interested_genres:
        split_genres = [g.strip() for g in genre.split('/')]
        for g in split_genres:
            genre_weights[g] = genre_weights.get(g, 0) + 1


    # print("USERID:", user_id)
    # print("new genre_weights:", genre_weights)
    print("updating genre_weights:", update_genre_weights(user_id, genre_weights))
    # print("retrieve gw:", retrieve_genre_weights(user_id))


def process_wishlist(user_id):
    to_read_shelf = get_unread_books(user_id)
    books_to_read = []
    print("To read:", to_read_shelf)
    for book in to_read_shelf:
        book_id = book["book_id"]
        book_obj = books_collection.find_one({"_id": book_id})
        if book_obj:
            books_to_read.append(book_obj)
    user = read_user(user_id)
    # print(books_to_read)
    if not user:
        print("USER NOT FOUND")
    for book in books_to_read:
        genres = book["genre_tags"]
        print("BOOK GENRES:", genres)
        weight_change = 0.5
        genre_weights = retrieve_genre_weights(user_id)
        if isinstance(genre_weights, str):
            genre_weights = {}  # Initialize if not found

        for genre in genres:
            if genre not in genre_weights:
                genre_weights[genre] = weight_change
            else:
                genre_weights[genre] += weight_change

        print("NEW genre weights:", genre_weights)
        print("UPDATING...:", update_genre_weights(user_id, genre_weights))

        # print(update_user_gw(user_id, genre_weights))
        print("genre weights:", retrieve_genre_weights(user_id))

        # Embedding update
        user_embedding = retrieve_embedding(user_id)  # Retrieve embedding from DB
        book_embedding = np.array(book["embedding"], dtype=np.float64)

        if isinstance(user_embedding, np.ndarray):
            pass  # Already a NumPy array, no conversion needed

        if user_embedding is None or len(user_embedding) == 0:
            print("empty user embedding")
            user_embedding = np.zeros_like(book_embedding)  # Handle missing embeddings

        if book_embedding is None or len(book_embedding) == 0:
            return

        # Compute new embedding
        new_embedding = (user_embedding + book_embedding) / 2
        # print(new_embedding)
        update_user_embedding(user_id, new_embedding.tolist())


def process_user_rating(user_id, book_id, rating):
    """Handles user book interactions and updates preferences."""
    if not rating:
        print("Book read but not rated by user.")
        return
    if rating not in ["pos", "neg", "mid"]:
        print("Invalid rating.")
        return

    # Fetch or create user
    user = read_user(user_id)
    if not user:
        print("USER NOT FOUND")

    book = books_collection.find_one({"_id": book_id})
    if not book:
        print(f"Book {book_id} not found in database.")
        return

    # Genre weight update
    genres = book.get("genre_tags", [])
    weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

    genre_weights = retrieve_genre_weights(user_id)
    if isinstance(genre_weights, str):
        genre_weights = {}  # Initialize if not found

    for genre in genres:
        genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

    # print(update_user_gw(user_id, genre_weights))
    # print("User new genre weights:", retrieve_genre_weights(user_id))
    update_genre_weights(user_id, genre_weights)
    # Embedding update
    if rating == "pos":
        user_embedding = retrieve_user_embedding(user_id)  # Retrieve embedding from DB
        book_embedding = np.array(book["embedding"], dtype=np.float64)

        if isinstance(user_embedding, np.ndarray):
            pass  # Already a NumPy array, no conversion needed

        if user_embedding is None or len(user_embedding) == 0:
            print("empty user embedding")
            user_embedding = np.zeros_like(book_embedding)  # Handle missing embeddings

        if book_embedding is None or len(book_embedding) == 0:
            return

        # Compute new embedding
        new_embedding = (user_embedding + book_embedding) / 2
        update_user_embedding(user_id, new_embedding.tolist())


# def update_user_gw(user_id, genre_weights):
#     """Update the user's genre weights in the database."""
#     redis_client.set(f"genre_weights:{user_id}", json.dumps(genre_weights))
#     update_genre_weights(user_id, genre_weights)


def update_user_embedding(user_id, new_embedding):
    """Update the user's embedding in the database or cache."""
    redis_client.set(f"user_embedding:{user_id}", json.dumps(new_embedding))
    update_embedding(user_id, new_embedding)


def retrieve_user_embedding(user_id):
    cache_key = f"user_embedding:{user_id}"
    cached_embedding = redis_client.get(cache_key)
    if cached_embedding:
        return np.array(json.loads(cached_embedding))
    user_embedding = retrieve_embedding(user_id)
    if user_embedding is None:  # Handle missing embeddings
        # raise ValueError(f"User embedding not found for user_id: {user_id}")
        user_embedding = np.zeros(384)
    redis_client.set(cache_key, json.dumps(user_embedding.tolist()), ex=3600)
    return user_embedding


# def get_all_books():
#     """Retrieve books from Redis instead of MongoDB."""
#     return list(books_collection.find({}))


def update_book_embeddings(books):
    if not isinstance(books, collections.abc.Iterable):
        print("Error: books is not an iterable collection")
        return []

    books_missing_embeddings = [
        book for book in books if "embedding" not in book or not book["embedding"]
    ]
    # print(f"Books missing embeddings: {len(books_missing_embeddings)}")

    if books_missing_embeddings:
        summaries = [book.get("summary", "") for book in books_missing_embeddings]
        embeddings = model.encode(summaries, convert_to_numpy=True)

        for book, embedding in zip(books_missing_embeddings, embeddings):
            result = books_collection.update_one(
                {"_id": book["_id"]}, {"$set": {"embedding": embedding.tolist()}}
            )
            print(
                f"Updated book {book['_id']}: {result.modified_count} document(s) updated"
            )


def generate_recs(user_id, top_n=6):
    print("USERID IN RECS:", user_id)
    user_embedding = retrieve_user_embedding(user_id)
    # print("user emb:", user_embedding)
    genre_weights = retrieve_genre_weights(user_id)
    # print("gw:", genre_weights)
    print("retrieving books...")
    books = book_collection.get_books()  # Get books from memory
    print(f"Total books retrieved: {len(books)}")

    update_book_embeddings(books)
    books_read = {book["book_id"] for book in retrieve_user_bookshelf(user_id)}
    books_to_read = {book["book_id"] for book in get_unread_books(user_id)}
    book_embeddings = np.array([np.array(book["embedding"]) for book in books])

    valid_books = []

    for book in books:
        if book["_id"] not in books_read and book["_id"] not in books_to_read:
            valid_books.append(book)

    # # Debugging output
    # print(
    #     f"user_embedding shape: {user_embedding.shape if user_embedding is not None else 'None'}"
    # )
    # print(
    #     f"book_embeddings shape: {book_embeddings.shape if book_embeddings is not None else 'None'}"
    # )

    print("VALID BOOKS:", len(valid_books))

    # Check if user_embedding is None or empty
    if user_embedding is None or user_embedding.size == 0:
        print("Error: user_embedding is empty or None")
        return []

    # Ensure user_embedding is 2D
    if user_embedding.ndim == 1:
        user_embedding = user_embedding.reshape(1, -1)

    # Check if book_embeddings is None or empty
    if book_embeddings is None or book_embeddings.size == 0:
        print("Error: book_embeddings is empty or None")
        return []

    # book_embeddings = np.array(book_embeddings, dtype=np.float64)  # Convert once after collecting

    # Debugging output
    # print(f"Number of books: {len(book_embeddings)}")
    # print(f"First few book embeddings: {book_embeddings[:5] if len(book_embeddings) > 0 else 'No embeddings'}")

    # similarities = cosine_similarity(user_embedding.reshape(1, -1), book_embeddings)[0]
    # recommendations = [(book, sim) for book, sim in zip(books, similarities) if book["_id"] not in books_read]
    # recommendations.sort(key=lambda x: x[1], reverse=True)

    # return [book for book, _ in recommendations[:top_n]]
    use_similarities = True
    if np.all(user_embedding == 0):
        use_similarities = False
    similarities = cosine_similarity(user_embedding.reshape(1, -1), book_embeddings)[0]

    recommendations = []
    # print("genre_weights:", genre_weights)
    
    if use_similarities:
        for book, sim in zip(valid_books, similarities):
            genre_score = sum(
                genre_weights.get(genre, 0) for genre in book.get("genre_tags", [])
            )
            total_score = sim + genre_score * 0.1  # Adjust weight factor as needed
            recommendations.append((book, total_score))
    else:
        # print("No embedding, just genres.")
        for book in valid_books:
            book_genres = [g.lower() for g in book.get("genre_tags", [])]
            genre_score = 0
            for genre, weight in genre_weights.items():
                genre_lower = genre.lower()
                if any(genre_lower in book_genre for book_genre in book_genres):
                    genre_score += weight
            # print("GENRE TAGS:", book.get("genre_tags", []))
            recommendations.append((book, genre_score))


    recommendations.sort(key=lambda x: x[1], reverse=True)
    book_scores = [score for _, score in recommendations[:5]]
    print(book_scores)
    best_books = [book for book, _ in recommendations[:2]]

    # Create a list of books to filter for duplicates
    remaining_books = [book for book, _ in recommendations[2:20]]

    # Filter out books that are considered duplicates (same author and similar title)
    filtered_books = []
    for book in remaining_books:
        duplicate_found = False
        for seen_book in best_books:
            if is_duplicate(book, seen_book):
                duplicate_found = True
                break
        if not duplicate_found:
            filtered_books.append(book)

    # Ensure we have enough books to randomly select
    if len(filtered_books) >= 4:
        random_books = random.sample(filtered_books, 4)
    else:
        random_books = filtered_books  # If fewer than 4 options, select all remaining books

    # Combine the best 2 books with the randomly selected 4 books
    final_recommendations = best_books + random_books

    return final_recommendations


# Function to normalize and clean up book titles
def normalize_title(title):
    # Remove common words like "Edition", "Tie-in", "Book X" etc.
    title = re.sub(r"\(.*\)", "", title)  # Remove anything inside parentheses
    title = re.sub(r"(Anniversary|Movie Tie-in|Bestselling|Special Edition|Collector's Edition)", "", title, flags=re.IGNORECASE)
    title = title.strip().lower()  # Convert to lowercase and strip leading/trailing spaces
    return title

# Function to check if two titles are similar using fuzzy matching
def are_titles_similar(title1, title2, threshold=50):
    title1_normalized = normalize_title(title1)
    title2_normalized = normalize_title(title2)
    
    # Use fuzzy matching to compare titles

    similarity_score = fuzz.ratio(title1_normalized, title2_normalized)
    # print(title1, "+", title2, " similarity=", similarity_score)
    return similarity_score >= threshold

def is_duplicate(book1, book2):
    title1, authors1 = book1['title'], book1['author']
    title2, authors2 = book2['title'], book2['author']
    
    # Normalize author lists (in case of varying author name formats)
    authors1 = [author.strip().lower() for author in authors1]
    authors2 = [author.strip().lower() for author in authors2]

    # Check if there is any overlap in authors (case-insensitive)
    if any(author in authors2 for author in authors1) or are_titles_similar(title1, title2):
        return True
    return False




def recommend_books(user_id):
    # print("1 ***************************")
    update_genre_weights(user_id, dict())
    # print("starting gw: ", retrieve_genre_weights(user_id))
    update_embedding(user_id, np.zeros(384))
    # print("starting embedding: ", retrieve_embedding(user_id))
    # print("2 ***************************")
    process_reading_history(user_id)
    # print("3 ***************************")
    process_wishlist(user_id)
    # print("4 ***************************")
    return generate_recs(user_id=user_id)

def onboarding_recommendations(user_id, interests):
    update_genre_weights_only(user_id, interests)
    return True


# Example usage:

# user_id = "67c64c27835dd5190e9d458b"
# process_reading_history(user_id)
# print(recommend_books(user_id))

# user_id = "67f58b311c43cef5572babc2"

# interested_genres = ["Science Fiction", "Fantasy", "Romance"]

# result = onboarding_recommendations(user_id, interested_genres)

# print("result:", result)
# print("recs being generated")
# print(recommend_books(user_id))
