import collections
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

#############################################################
# WITHOUT DB ################################################
class BookRecommenderNoDB:
    def __init__(self):
        self.user_profiles = defaultdict(
            lambda: {
                "genre_weights": defaultdict(float),
                "embedding_vector": None,
                "read_books": {},
            }
        )
        self.book_data = {}  # Stores book metadata {book_id: {"genres": [...], "embedding": np.array, "summary": str, "summary_embedding": np.array}}
        self.valid_ratings = ["pos", "neg", "mid"]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def process_summary(self, summary):
        """Converts a book summary into an embedding representation using Sentence Transformers."""
        return self.model.encode(summary)

    def add_book(self, book_id, genres, summary):
        """Registers a book with genres and raw summary, processing summary into an embedding."""
        summary_embedding = self.process_summary(summary)

        # Store book metadata
        self.book_data[book_id] = {
            "genres": genres,
            "summary": summary,
            "summary_embedding": summary_embedding,
        }

    def update_genre_weights(self, user_id, book_id, rating):
        """Adjusts genre preferences based on user rating"""
        genres = self.book_data[book_id]["genres"]
        weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

        for genre in genres:
            self.user_profiles[user_id]["genre_weights"][genre] += weight_change

    def update_embedding_vector(self, user_id, book_id):
        """Updates the user's preference embedding by averaging book and summary embeddings"""

        summary_vector = self.book_data[book_id]["summary_embedding"]

        if self.user_profiles[user_id]["embedding_vector"] is None:
            self.user_profiles[user_id]["embedding_vector"] = summary_vector
        else:
            self.user_profiles[user_id]["embedding_vector"] = (
                self.user_profiles[user_id]["embedding_vector"] + summary_vector
            ) / 2

    def process_user_rating(self, user_id, book_id, rating):
        """Handles user book interactions and updates preferences"""
        if rating not in self.valid_ratings:
            print("NOT A VALID RATING")
            return

        self.user_profiles[user_id]["read_books"][book_id] = rating

        self.update_genre_weights(user_id, book_id, rating)
        if rating == "pos":
            self.update_embedding_vector(user_id, book_id)

    def recommend_books(self, user_id, top_n=3):
        """Recommends books based on user embedding similarity & genre preference"""
        user_vector = self.user_profiles[user_id]["embedding_vector"]

        if user_vector is None:
            return []

        book_scores = []
        for book_id, book_info in self.book_data.items():
            if book_id not in self.user_profiles[user_id]["read_books"]:
                summary_vector = book_info["summary_embedding"]
                similarity = cosine_similarity(
                    user_vector.reshape(1, -1), summary_vector.reshape(1, -1)
                )[0][0]

                # Compute genre-based score
                genre_score = sum(
                    self.user_profiles[user_id]["genre_weights"].get(g, 0)
                    for g in book_info["genres"]
                )
                final_score = similarity + genre_score  # Weighted sum

                book_scores.append((book_id, final_score))

        book_scores.sort(key=lambda x: x[1], reverse=True)
        return [book[0] for book in book_scores[:top_n]]




#############################################################
# WITH DB CONNECTION ########################################
from models.user_bookshelf import retrieve_user_bookshelf
from database import collections
# from pymongo import MongoClient
# from bson.objectid import ObjectId
from models.books import books_collection, update_book_embedding, read_book_field


from models.users import (
    read_user,
    update_genre_weights,
    retrieve_genre_weights,
    update_embedding,
    retrieve_embedding,
)


class BookRecommender:
    def __init__(self):
        # # MongoDB setup - is this needed?
        # self.client = MongoClient("mongodb://localhost:27017/")
        # self.db = self.client["book_recommendation"]
        # self.books_collection = self.db["books"]

        self.valid_ratings = ["pos", "neg", "mid"]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def process_summary(self, summary):
        """Converts a book summary into an embedding representation using Sentence Transformers."""
        return self.model.encode(summary)

    def update_book_embedding_in_db(self, book_id):
        summary = read_book_field(book_id, "summary")
        encoded_summary = self.process_summary(summary)
        update_book_embedding(book_id, encoded_summary)

    def process_reading_history(self, user_id):
        books_read = retrieve_user_bookshelf(user_id)
        print(books_read)
        for book in books_read:
            book_id = book['book_id']
            rating = book['rating']
            print("book id:", book_id)
            print("rating:", rating)
            self.process_user_rating(user_id, book_id, rating)



    # MAY NOT BE NEEDED: ADD BOOK FUNCTION

    # def add_book(self, book_id, genres, summary):
    #     """Adds a book to DB with genres and embedding."""
    #     summary_embedding = self.process_summary(summary)

    #     self.books_collection.update_one(
    #         {"_id": book_id},
    #         {
    #             "$set": {
    #                 "genres": genres,
    #                 "summary": summary,
    #                 "summary_embedding": summary_embedding.tolist(),
    #             }
    #         },
    #         upsert=True,
    #     )

    def process_user_rating(self, user_id, book_id, rating):
        """Handles user book interactions and updates preferences."""
        if rating not in self.valid_ratings:
            print("Rating:",  rating)
            print("NOT A VALID RATING")
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
        genres = book["genre_tags"]
        weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

        genre_weights = retrieve_genre_weights(user_id)
        if isinstance(genre_weights, str):
            genre_weights = {}  # Initialize if not found

        for genre in genres:
            genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

        update_genre_weights(user_id, genre_weights)

        # Embedding update
        if rating == "pos":
            user_embedding = retrieve_embedding(user_id)  # Retrieve embedding from DB
            book_embedding = np.array(book["embedding"], dtype=np.float64)

            if isinstance(user_embedding, np.ndarray):
                pass  # Already a NumPy array, no conversion needed
           
            if user_embedding is None or len(user_embedding) == 0:
                user_embedding = np.zeros_like(book_embedding)  # Handle missing embeddings

            # Compute new embedding
            new_embedding = (user_embedding + book_embedding) / 2
            update_embedding(user_id, new_embedding.tolist())

    # def process_user_rating(self, user_id, book_id, rating):
    #     """Handles user book interactions and updates preferences."""
    #     if rating not in self.valid_ratings:
    #         print("NOT A VALID RATING")
    #         return

    #     # Fetch or create user
    #     user = read_user(user_id)
    #     if not user:
    #         # create_user(username=username, first_name="", last_name="", email_address="", oauth={}, profile_image="", interests=[], demographics={})
    #         # user = get_user(username)
    #         print("USER NOT FOUND")

    #     book = books_collection.find_one({"_id": book_id})
    #     if not book:
    #         print(f"Book {book_id} not found in database.")
    #         return

    #     # genre weight update
    #     genres = book["genre_tags"]
    #     weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

    #     genre_weights = retrieve_genre_weights(user_id)
    #     if isinstance(genre_weights, str):
    #         genre_weights = {}  # do not exist

    #     for genre in genres:
    #         genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

    #     update_genre_weights(user_id, genre_weights)

    #     # # embedding update
    #     # if rating == "pos":
    #     #     user_embedding = np.array(retrieve_embedding(user_id))
    #     #     book_embedding = np.array(book["embedding"])

    #     #     if user_embedding.size == 0:
    #     #         new_embedding = book_embedding
    #     #     else:
    #     #         new_embedding = (
    #     #             user_embedding + book_embedding
    #     #         ) / 2  # average - change later if needed?

    #     #     update_embedding(user_id, new_embedding.tolist())

    #     # embedding update
    #     if rating == "pos":
    #         user_embedding = np.array(retrieve_embedding(user_id))
    #         if not user_embedding:  # Covers both None and empty string cases
    #             user_embedding = np.zeros_like(book["embedding"])  # Initialize with zeros
    #         else:
    #             try:
    #                 user_embedding = np.array(json.loads(user_embedding), dtype=np.float64)
    #             except json.JSONDecodeError:
    #                 print(f"Invalid embedding for user {user_id}: {user_embedding}")  # Debugging print
    #                 user_embedding = np.zeros_like(book["embedding"])  # Default to zeros

    #         user_embedding = retrieve_embedding(user_id)
    #         book_embedding = np.array(book["embedding"], dtype=np.float64)
    #         if not book_embedding:
    #             self.update_book_embedding_in_db(book_id, book["summary"])
    #             if not book_embedding:
    #                 pass 
    #         if isinstance(user_embedding, str):  # Convert if stored as a string
    #             user_embedding = np.array(json.loads(user_embedding), dtype=np.float64)
    #         elif user_embedding is None or len(user_embedding) == 0:  # Handle missing embeddings
    #             user_embedding = np.zeros_like(book_embedding)

    #         # Compute new embedding
    #         new_embedding = (user_embedding + book_embedding) / 2
    #         update_embedding(user_id, new_embedding.tolist())

    def recommend_books(self, user_id, top_n=5):
        """Recommends books based on user embedding similarity & genre preference."""
        user = read_user(user_id)
        if not user:
            print("NO USER FOUND")
            return []

        # Retrieve user embedding and ensure it's a NumPy array
        user_vector = np.array(retrieve_embedding(user_id))  # Ensure it's a numpy array
        if user_vector.ndim == 1:  # If it's a 1D array, check for NaN or empty
            if user_vector.size == 0 or np.any(np.isnan(user_vector)):  # Check for NaN or empty user_vector
                print("USER HAS NO READING HISTORY or NaN in user embedding")
                return []

        books = list(books_collection.find({}))
        book_scores = []

        genre_weights = retrieve_genre_weights(user_id)
        if isinstance(genre_weights, str):
            genre_weights = {}  # Handle error case

        for book in books:
            book_id = book["_id"]
            
            # Retrieve and validate summary embedding
            summary_embedding = read_book_field(book_id, "embedding")
            if summary_embedding is None or len(summary_embedding) == 0:  # Handle missing or empty embedding
                print(f"Book {book_id} has no embedding, attempting to update.")
                self.update_book_embedding_in_db(book_id)
                
            if summary_embedding is None or len(summary_embedding) == 0:  # Handle missing or empty embedding
                print(f"Book {book_id} still has no embedding, skipping.")
            # Convert summary_embedding to numpy array and check for NaN
            summary_embedding = np.array(summary_embedding)
            if np.any(np.isnan(summary_embedding)):  # Check for NaN in book embedding
                
                print(f"Book {book_id} has NaN in embedding, replacing with zeros.")
                summary_embedding = np.zeros_like(user_vector)  # Replace with zeros

            # Ensure user_vector and summary_embedding are 2D before similarity calculation
            user_vector = np.nan_to_num(user_vector)  # Replace NaN in user_vector with zeros
            summary_embedding = np.nan_to_num(summary_embedding)  # Replace NaN in book embedding with zeros

            # Compute cosine similarity
            similarity = cosine_similarity(
                user_vector.reshape(1, -1), summary_embedding.reshape(1, -1)
            )[0][0]

            genres = read_book_field(book_id, "genres")
            genre_score = sum(genre_weights.get(g, 0) for g in genres)
            final_score = similarity + genre_score  # Weighted sum

            book_scores.append((book_id, final_score))

        book_scores.sort(key=lambda x: x[1], reverse=True)
        return [book[0] for book in book_scores[:top_n]]

#############################################################
# MAIN ######################################################

books_collection = collections["Books"]
users_collection = collections["Users"]
user_bookshelf_collection = collections["User_Bookshelf"]
recommender = BookRecommender()

# Katelyn's user ID = 67c64c27835dd5190e9d458b
id = '67c64c27835dd5190e9d458b'

recommender.process_reading_history(id)
recs = recommender.recommend_books(id)
print(f"Recommended books: {recs}")

if __name__ == "__main__":
    # recommender = BookRecommenderNoDB()

    # recommender.add_book(
    #     "1984",
    #     ["dystopian", "political fiction"],
    #     "A totalitarian regime uses surveillance and control to oppress its people.",
    # )
    # recommender.add_book(
    #     "Pride and Prejudice",
    #     ["romance", "historical"],
    #     "Elizabeth Bennet navigates issues of manners, upbringing, and marriage in 19th-century England.",
    # )
    # recommender.add_book(
    #     "Dune",
    #     ["sci-fi", "adventure"],
    #     "Paul Atreides becomes embroiled in political and mystical conflicts over a desert planet and its valuable spice.",
    # )
    # recommender.add_book(
    #     "The Hobbit",
    #     ["fantasy", "adventure"],
    #     "Bilbo Baggins embarks on a journey to reclaim a lost dwarven kingdom.",
    # )
    # recommender.add_book(
    #     "The Shining",
    #     ["horror", "psychological"],
    #     "A writer and his family stay in a haunted hotel over the winter, descending into madness.",
    # )
    # recommender.add_book(
    #     "Dracula",
    #     ["horror", "classic"],
    #     "The story of Count Dracula's attempt to move from Transylvania to England and his battle with Van Helsing.",
    # )
    # recommender.add_book(
    #     "The Road",
    #     ["post-apocalyptic", "drama"],
    #     "A father and son journey across a desolate America in search of safety.",
    # )
    # recommender.add_book(
    #     "The Name of the Wind",
    #     ["fantasy", "adventure"],
    #     "A gifted young man grows up to become a legendary magician.",
    # )
    # recommender.add_book(
    #     "Educated",
    #     ["memoir", "non-fiction"],
    #     "A woman who grows up in a survivalist family in rural Idaho strives for education and self-discovery.",
    # )
    # recommender.add_book(
    #     "The Fault in Our Stars",
    #     ["romance", "realistic fiction"],
    #     "Two teenagers with cancer find love and meaning in their lives despite their struggles.",
    # )
    # recommender.add_book(
    #     "Becoming",
    #     ["biography", "non-fiction"],
    #     "Michelle Obama's journey from childhood to First Lady of the United States.",
    # )
    # recommender.add_book(
    #     "Atomic Habits",
    #     ["self-help", "non-fiction"],
    #     "A guide to forming good habits and breaking bad ones through small changes.",
    # )
    # recommender.add_book(
    #     "Where the Crawdads Sing",
    #     ["mystery", "realistic fiction"],
    #     "A girl raised in the marshes of North Carolina becomes entangled in a murder investigation.",
    # )
    # recommender.add_book(
    #     "The Night Circus",
    #     ["fantasy", "romance"],
    #     "Two young illusionists compete in a magical circus that appears only at night.",
    # )
    # recommender.add_book(
    #     "The Alchemist",
    #     ["adventure", "philosophical"],
    #     "A shepherd embarks on a journey to discover his personal legend.",
    # )
    # recommender.add_book(
    #     "Moby Dick",
    #     ["adventure", "classic"],
    #     "A whaling voyage turns into an obsessive hunt for a great white whale.",
    # )
    # recommender.add_book(
    #     "Frankenstein",
    #     ["horror", "classic"],
    #     "A scientist creates a living being, leading to tragic consequences.",
    # )
    # recommender.add_book(
    #     "Brave New World",
    #     ["dystopian", "sci-fi"],
    #     "A future society controls its citizens through genetic engineering and conditioning.",
    # )
    # recommender.add_book(
    #     "To Kill a Mockingbird",
    #     ["historical", "drama"],
    #     "A young girl learns about racism and justice in the American South.",
    # )
    # recommender.add_book(
    #     "It",
    #     ["horror", "thriller", "classic"],
    #     "A group of childhood friends must confront a malevolent, shape-shifting entity. ",
    # )

    # users = {
    #     "user1": [
    #         ("1984", "pos"),
    #         ("Dune", "neg"),
    #         ("The Hobbit", "pos"),
    #         ("Moby Dick", "mid"),
    #     ],
    #     "user2": [
    #         ("Pride and Prejudice", "pos"),
    #         ("The Name of the Wind", "pos"),
    #         ("Dracula", "neg"),
    #         ("Frankenstein", "pos"),
    #     ],
    #     "user3": [
    #         ("The Road", "pos"),
    #         ("The Shining", "neg"),
    #         ("Dune", "pos"),
    #         ("Brave New World", "pos"),
    #     ],
    #     "user4": [
    #         ("Dracula", "pos"),
    #         ("The Hobbit", "neg"),
    #         ("1984", "pos"),
    #         ("To Kill a Mockingbird", "pos"),
    #     ],
    #     "user5": [("It", "pos")],
    #     "user6": [("The Night Circus", "neg")],
    # }
    # #
    # # Recommended books for user1: ['The Night Circus', 'The Name of the Wind', 'Dracula', 'Atomic Habits', 'Educated']
    # # Recommended books for user2: ['The Hobbit', 'The Night Circus', 'Moby Dick', 'Dune', 'The Alchemist']
    # # Recommended books for user3: ['The Hobbit', 'The Alchemist', 'To Kill a Mockingbird', 'The Name of the Wind', '1984']
    # # Recommended books for user4: ['Frankenstein', 'The Road', 'The Shining', 'Pride and Prejudice', 'Brave New World']
    # #

    # for user_id, ratings in users.items():
    #     for book_id, rating in ratings:
    #         recommender.process_user_rating(user_id, book_id, rating)


    books_collection = collections["Books"]
    users_collection = collections["Users"]
    user_bookshelf_collection = collections["UserBookshelf"]
    recommender = BookRecommender()

    # Katelyn's user ID = 67c64c27835dd5190e9d458b
    id = "67c64c27835dd5190e9d458b"
    recommender.process_reading_history(id)
    recs = recommender.recommend_books(id)
    print(f"Recommended books: {recs}")


    # for user_id in users.keys():
    #     recommendations = recommender.recommend_books(user_id, top_n=5)
    #     print(f"Recommended books for {user_id}: {recommendations}")
