# import numpy as np
# from collections import defaultdict
# from sklearn.metrics.pairwise import cosine_similarity


# # BOOK RECOMMENDER WITHOUT SUMMARY TOKENIZATION
# class BookRecommender:
#     def __init__(self):
#         self.user_profiles = defaultdict(lambda: {
#             "genre_weights": defaultdict(float),
#             "embedding_vector": None,
#             "read_books": {}
#         })
#         self.book_data = {}  # Stores book metadata {book_id: {"genres": [...], "embedding": np.array}}
#         self.valid_ratings = ['pos', 'neg', 'mid']

#     def add_book(self, book_id, genres):
#         """Registers a book with genres and precomputed embedding"""
        
#         # GENERATE EMBEDDING
#         book_embedding = np.random.rand(300)
#         self.book_data[book_id] = {"genres": genres, "embedding": np.array(book_embedding)}

#     def get_book_genres(self, book_id):
#         """Retrieves genres of a book"""
#         return self.book_data.get(book_id, {}).get("genres", [])

#     def get_book_embedding(self, book_id):
#         """Retrieves embedding vector of a book"""
#         return self.book_data.get(book_id, {}).get("embedding", np.zeros(300))  # Default 300-dim zero vector

#     def update_genre_weights(self, user_id, book_id, rating):
#         """Adjusts genre preferences based on user rating"""
#         genres = self.get_book_genres(book_id)
#         weight_change = 0  # Default (neutral)

#         if rating == "pos":
#             weight_change = 1  # Increase preference
#         elif rating == "neg":
#             weight_change = -1  # Decrease preference

#         for genre in genres:
#             self.user_profiles[user_id]["genre_weights"][genre] += weight_change

#     def update_embedding_vector(self, user_id, book_id):
#         """Updates the user's preference embedding by averaging book embeddings"""
#         book_vector = self.get_book_embedding(book_id)

#         if self.user_profiles[user_id]["embedding_vector"] is None:
#             self.user_profiles[user_id]["embedding_vector"] = book_vector
#         else:
#             self.user_profiles[user_id]["embedding_vector"] = (
#                 self.user_profiles[user_id]["embedding_vector"] + book_vector
#             ) / 2

#     def process_user_rating(self, user_id, book_id, rating):
#         """Handles user book interactions and updates preferences"""

#         if rating not in self.valid_ratings:
#             print("NOT A VALID RATING")
#             pass
        
#         self.user_profiles[user_id]["read_books"][book_id] = rating

#         self.update_genre_weights(user_id, book_id, rating)
#         self.update_embedding_vector(user_id, book_id)

#     def recommend_books(self, user_id, top_n=3):
#         """Recommends books based on user embedding similarity & genre preference"""
#         user_vector = self.user_profiles[user_id]["embedding_vector"]

#         ## UPDATE LATER based on initial diagnostic quiz
#         if user_vector is None:
#             return []

#         book_scores = []
#         for book_id, book_info in self.book_data.items():
#             if book_id not in self.user_profiles[user_id]["read_books"]:  # Avoid recommending read books
#                 book_vector = book_info["embedding"]
#                 similarity = cosine_similarity(user_vector.reshape(1, -1), book_vector.reshape(1, -1))[0][0]

#                 # Compute genre-based score
#                 genre_score = sum(self.user_profiles[user_id]["genre_weights"].get(g, 0) for g in book_info["genres"])
#                 final_score = similarity + genre_score  # Weighted sum

#                 book_scores.append((book_id, final_score))

#         # Sort and return top recommendations
#         book_scores.sort(key=lambda x: x[1], reverse=True)
#         return [book[0] for book in book_scores[:top_n]]


# # Initialize the recommender system
# recommender = BookRecommender()

# # Add books to the system
# recommender.add_book("Dune", ["Sci-Fi", "Adventure"]) # LIKED
# recommender.add_book("The Hobbit", ["Fantasy", "Adventure"]) # DID NOT LIKE

# recommender.add_book("Foundation", ["Sci-Fi"])
# recommender.add_book("I, Robot", ["Sci-Fi", "Adventure"])
# recommender.add_book("Star Wars", ["Sci-Fi", "Fantasy"])
# recommender.add_book("The Fellowship of the Ring", ["Fantasy", "Adventure"])
# recommender.add_book("Lessons in Chemistry", ["Romance"])
# recommender.add_book("Oryx and Crake", ["Sci-Fi", "Romance"])
# recommender.add_book("Ender's Game", ["Sci-Fi"])

# # User reads & rates books
# recommender.process_user_rating("User1", "Dune", "pos")
# recommender.process_user_rating("User1", "The Hobbit", "neg")
# recommender.process_user_rating("User1", "Lessons in Chemistry", "neg")

# # print User info
# print("User1: ", recommender.user_profiles["User1"])

# # Get recommendations for the user
# print("Recommended books:", recommender.recommend_books("User1"))



import numpy as np
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

class BookRecommender:
    def __init__(self):
        self.user_profiles = defaultdict(lambda: {
            "genre_weights": defaultdict(float),
            "embedding_vector": None,
            "read_books": {}
        })
        self.book_data = {}  # Stores book metadata {book_id: {"genres": [...], "embedding": np.array, "summary": str, "summary_embedding": np.array}}
        self.valid_ratings = ['pos', 'neg', 'mid']
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def process_summary(self, summary):
        """Converts a book summary into an embedding representation using Sentence Transformers."""
        return self.model.encode(summary)

    def add_book(self, book_id, genres, summary):
        """Registers a book with genres and raw summary, processing summary into an embedding."""
        book_embedding = np.random.rand(384)  # Replace with actual metadata-based embedding if needed
        summary_embedding = self.process_summary(summary)
        
        # Store book metadata
        self.book_data[book_id] = {
            "genres": genres,
            "embedding": book_embedding,
            "summary": summary,
            "summary_embedding": summary_embedding
        }

    def update_genre_weights(self, user_id, book_id, rating):
        """Adjusts genre preferences based on user rating"""
        genres = self.book_data[book_id]["genres"]
        weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

        for genre in genres:
            self.user_profiles[user_id]["genre_weights"][genre] += weight_change

    def update_embedding_vector(self, user_id, book_id):
        """Updates the user's preference embedding by averaging book and summary embeddings"""
        book_vector = self.book_data[book_id]["embedding"]
        summary_vector = self.book_data[book_id]["summary_embedding"]
        combined_vector = (book_vector + summary_vector) / 2

        if self.user_profiles[user_id]["embedding_vector"] is None:
            self.user_profiles[user_id]["embedding_vector"] = combined_vector
        else:
            self.user_profiles[user_id]["embedding_vector"] = (
                self.user_profiles[user_id]["embedding_vector"] + combined_vector
            ) / 2

    def process_user_rating(self, user_id, book_id, rating):
        """Handles user book interactions and updates preferences"""
        if rating not in self.valid_ratings:
            print("NOT A VALID RATING")
            return
        
        self.user_profiles[user_id]["read_books"][book_id] = rating

        self.update_genre_weights(user_id, book_id, rating)
        self.update_embedding_vector(user_id, book_id)

    def recommend_books(self, user_id, top_n=3):
        """Recommends books based on user embedding similarity & genre preference"""
        user_vector = self.user_profiles[user_id]["embedding_vector"]

        if user_vector is None:
            return []

        book_scores = []
        for book_id, book_info in self.book_data.items():
            if book_id not in self.user_profiles[user_id]["read_books"]:
                book_vector = book_info["embedding"]
                summary_vector = book_info["summary_embedding"]
                combined_vector = (book_vector + summary_vector) / 2
                similarity = cosine_similarity(user_vector.reshape(1, -1), combined_vector.reshape(1, -1))[0][0]

                # Compute genre-based score
                genre_score = sum(self.user_profiles[user_id]["genre_weights"].get(g, 0) for g in book_info["genres"])
                final_score = similarity + genre_score  # Weighted sum

                book_scores.append((book_id, final_score))

        book_scores.sort(key=lambda x: x[1], reverse=True)
        return [book[0] for book in book_scores[:top_n]]


if __name__ == "__main__":
    recommender = BookRecommender()


    recommender.add_book("1984", ["dystopian", "political fiction"], "A totalitarian regime uses surveillance and control to oppress its people.")
    recommender.add_book("Pride and Prejudice", ["romance", "historical"], "Elizabeth Bennet navigates issues of manners, upbringing, and marriage in 19th-century England.")
    recommender.add_book("Dune", ["sci-fi", "adventure"], "Paul Atreides becomes embroiled in political and mystical conflicts over a desert planet and its valuable spice.")
    recommender.add_book("The Hobbit", ["fantasy", "adventure"], "Bilbo Baggins embarks on a journey to reclaim a lost dwarven kingdom.")
    recommender.add_book("The Shining", ["horror", "psychological"], "A writer and his family stay in a haunted hotel over the winter, descending into madness.")
    recommender.add_book("Dracula", ["horror", "classic"], "The story of Count Dracula's attempt to move from Transylvania to England and his battle with Van Helsing.")
    recommender.add_book("The Road", ["post-apocalyptic", "drama"], "A father and son journey across a desolate America in search of safety.")
    recommender.add_book("The Name of the Wind", ["fantasy", "adventure"], "A gifted young man grows up to become a legendary magician.")
    recommender.add_book("Educated", ["memoir", "non-fiction"], "A woman who grows up in a survivalist family in rural Idaho strives for education and self-discovery.")
    recommender.add_book("The Fault in Our Stars", ["romance", "realistic fiction"], "Two teenagers with cancer find love and meaning in their lives despite their struggles.")
    recommender.add_book("Becoming", ["biography", "non-fiction"], "Michelle Obama's journey from childhood to First Lady of the United States.")
    recommender.add_book("Atomic Habits", ["self-help", "non-fiction"], "A guide to forming good habits and breaking bad ones through small changes.")
    recommender.add_book("Where the Crawdads Sing", ["mystery", "realistic fiction"], "A girl raised in the marshes of North Carolina becomes entangled in a murder investigation.")
    recommender.add_book("The Night Circus", ["fantasy", "romance"], "Two young illusionists compete in a magical circus that appears only at night.")
    recommender.add_book("The Alchemist", ["adventure", "philosophical"], "A shepherd embarks on a journey to discover his personal legend.")
    recommender.add_book("Moby Dick", ["adventure", "classic"], "A whaling voyage turns into an obsessive hunt for a great white whale.")
    recommender.add_book("Frankenstein", ["horror", "classic"], "A scientist creates a living being, leading to tragic consequences.")
    recommender.add_book("Brave New World", ["dystopian", "sci-fi"], "A future society controls its citizens through genetic engineering and conditioning.")
    recommender.add_book("To Kill a Mockingbird", ["historical", "drama"], "A young girl learns about racism and justice in the American South.")
    
    users = {"user1": [("1984", "pos"), ("Dune", "neg"), ("The Hobbit", "pos"), ("Moby Dick", "mid")],
             "user2": [("Pride and Prejudice", "pos"), ("The Name of the Wind", "pos"), ("Dracula", "neg"), ("Frankenstein", "pos")],
             "user3": [("The Road", "pos"), ("The Shining", "neg"), ("Dune", "pos"), ("Brave New World", "pos")],
             "user4": [("Dracula", "pos"), ("The Hobbit", "neg"), ("1984", "pos"), ("To Kill a Mockingbird", "pos")]
    }

    
    for user_id, ratings in users.items():
        for book_id, rating in ratings:
            recommender.process_user_rating(user_id, book_id, rating)
    
    for user_id in users.keys():
        recommendations = recommender.recommend_books(user_id, top_n=5)
        print(f"Recommended books for {user_id}: {recommendations}")