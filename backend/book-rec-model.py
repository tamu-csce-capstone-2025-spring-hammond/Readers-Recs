import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

# CHANGE TO pos, neg, mid

class BookRecommender:
    def __init__(self):
        self.user_profiles = defaultdict(lambda: {
            "genre_weights": defaultdict(float),
            "embedding_vector": None,
            "read_books": {}
        })
        self.book_data = {}  # Stores book metadata {book_id: {"genres": [...], "embedding": np.array}}
        self.valid_ratings = ['pos', 'neg', 'mid']

    def add_book(self, book_id, genres, embedding):
        """Registers a book with genres and precomputed embedding"""
        self.book_data[book_id] = {"genres": genres, "embedding": np.array(embedding)}

    def get_book_genres(self, book_id):
        """Retrieves genres of a book"""
        return self.book_data.get(book_id, {}).get("genres", [])

    def get_book_embedding(self, book_id):
        """Retrieves embedding vector of a book"""
        return self.book_data.get(book_id, {}).get("embedding", np.zeros(300))  # Default 300-dim zero vector

    def update_genre_weights(self, user_id, book_id, rating):
        """Adjusts genre preferences based on user rating"""
        genres = self.get_book_genres(book_id)
        weight_change = 0  # Default (neutral)

        if rating == "pos":
            weight_change = 1  # Increase preference
        elif rating == "neg":
            weight_change = -1  # Decrease preference

        for genre in genres:
            self.user_profiles[user_id]["genre_weights"][genre] += weight_change

    def update_embedding_vector(self, user_id, book_id):
        """Updates the user's preference embedding by averaging book embeddings"""
        book_vector = self.get_book_embedding(book_id)

        if self.user_profiles[user_id]["embedding_vector"] is None:
            self.user_profiles[user_id]["embedding_vector"] = book_vector
        else:
            self.user_profiles[user_id]["embedding_vector"] = (
                self.user_profiles[user_id]["embedding_vector"] + book_vector
            ) / 2

    def process_user_rating(self, user_id, book_id, rating):
        """Handles user book interactions and updates preferences"""

        if rating not in self.valid_ratings:
            print("NOT A VALID RATING")
            pass
        
        self.user_profiles[user_id]["read_books"][book_id] = rating

        self.update_genre_weights(user_id, book_id, rating)
        self.update_embedding_vector(user_id, book_id)

    def recommend_books(self, user_id, top_n=3):
        """Recommends books based on user embedding similarity & genre preference"""
        user_vector = self.user_profiles[user_id]["embedding_vector"]

        ## UPDATE LATER based on initial diagnostic quiz
        if user_vector is None:
            return []

        book_scores = []
        for book_id, book_info in self.book_data.items():
            if book_id not in self.user_profiles[user_id]["read_books"]:  # Avoid recommending read books
                book_vector = book_info["embedding"]
                similarity = cosine_similarity(user_vector.reshape(1, -1), book_vector.reshape(1, -1))[0][0]

                # Compute genre-based score
                genre_score = sum(self.user_profiles[user_id]["genre_weights"].get(g, 0) for g in book_info["genres"])
                final_score = similarity + genre_score  # Weighted sum

                book_scores.append((book_id, final_score))

        # Sort and return top recommendations
        book_scores.sort(key=lambda x: x[1], reverse=True)
        return [book[0] for book in book_scores[:top_n]]


# Initialize the recommender system
recommender = BookRecommender()

# Add books to the system
recommender.add_book("Dune", ["Sci-Fi", "Adventure"], np.random.rand(300)) # LIKED
recommender.add_book("The Hobbit", ["Fantasy", "Adventure"], np.random.rand(300)) # DID NOT LIKE

recommender.add_book("Foundation", ["Sci-Fi"], np.random.rand(300))
recommender.add_book("I, Robot", ["Sci-Fi", "Adventure"], np.random.rand(300))
recommender.add_book("Star Wars", ["Sci-Fi", "Fantasy"], np.random.rand(300))
recommender.add_book("The Fellowship of the Ring", ["Fantasy", "Adventure"], np.random.rand(300))
recommender.add_book("Lessons in Chemistry", ["Romance"], np.random.rand(300))
recommender.add_book("Oryx and Crake", ["Sci-Fi", "Romance"], np.random.rand(300))
recommender.add_book("Ender's Game", ["Sci-Fi"], np.random.rand(300))

# User reads & rates books
recommender.process_user_rating("User1", "Dune", "pos")
recommender.process_user_rating("User1", "The Hobbit", "neg")
recommender.process_user_rating("User1", "Lessons in Chemistry", "neg")

# print User info
print("User1: ", recommender.user_profiles["User1"])

# Get recommendations for the user
print("Recommended books:", recommender.recommend_books("User1"))