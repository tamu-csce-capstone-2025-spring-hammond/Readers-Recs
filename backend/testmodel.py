# import random
# import numpy as np
# # from models.user_bookshelf import retrieve_user_bookshelf
# from database import collections
# # from schemas import UserBookshelfSchema 
# from models.books import books_collection, read_book_field
# from recmodel import update_book_embeddings, is_duplicate
# from sklearn.metrics.pairwise import cosine_similarity
# from models.users import retrieve_genre_weights


# def split_user_bookshelf(user_id):
#     user_bookshelf_collection = collections["User_Bookshelf"]
#     full_shelf = list(user_bookshelf_collection.find({"user_id": user_id}))
#     print(len(full_shelf))
#     valid_books = [book for book in full_shelf if book["status"] in ["read", "currently-reading", "to-read"]]

#     if len(valid_books) < 2:
#         print(f"User {user_id} does not have enough valid books to split.")
#         return [], []

#     random.shuffle(valid_books)
#     midpoint = len(valid_books) // 2
#     return valid_books[:midpoint], valid_books[midpoint:]


# def simulate_onboarding(user_id, training_books):
#     genre_weights = retrieve_genre_weights(user_id)
#     user_embedding = np.zeros(384)
#     book_objs = []

#     for book_entry in training_books:
#         rating = book_entry.get("rating", "")
#         if not rating:
#             continue

#         book = books_collection.find_one({"_id": book_entry["book_id"]})
#         if not book:
#             continue

#         if rating not in ["pos", "neg", "mid"]:
#             continue

#         # Update genre weights
#         genres = book.get("genre_tags", [])
#         weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0
#         for genre in genres:
#             genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

#         # Update user embedding for positive ratings
#         if rating == "pos" and "embedding" in book and book["embedding"]:
#             user_embedding += np.array(book["embedding"])
#             book_objs.append(book)

#     # Finalize embedding
#     if book_objs:
#         user_embedding /= len(book_objs)

#     return user_embedding, genre_weights

# def process_user_rating(user_embed, user_genweight, book_id, rating):
#     """Handles user book interactions and updates preferences."""
#     if not rating:
#         print("Book read but not rated by user.")
#         return
#     if rating not in ["pos", "neg", "mid"]:
#         print("Invalid rating.")
#         return

#     # Fetch or create user
#     # user = read_user(user_id)
#     # if not user:
#     #     print("USER NOT FOUND")

#     book = books_collection.find_one({"_id": book_id})
#     if not book:
#         print(f"Book {book_id} not found in database.")
#         return

#     # Genre weight update
#     genres = book.get("genre_tags", [])
#     weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

#     genre_weights = user_genweight
#     if isinstance(genre_weights, str):
#         genre_weights = {}  # Initialize if not found

#     for genre in genres:
#         genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

#     # print(update_user_gw(user_id, genre_weights))
#     # print("User new genre weights:", retrieve_genre_weights(user_id))
#     # update_genre_weights(user_id, genre_weights)
#     # Embedding update
#     if rating == "pos":
#         user_embedding = user_embed  # Retrieve embedding from DB
#         book_embedding = np.array(book["embedding"], dtype=np.float64)

#         if isinstance(user_embedding, np.ndarray):
#             pass  # Already a NumPy array, no conversion needed

#         if user_embedding is None or len(user_embedding) == 0:
#             print("empty user embedding")
#             user_embedding = np.zeros_like(book_embedding)  # Handle missing embeddings

#         if book_embedding is None or len(book_embedding) == 0:
#             return

#         # Compute new embedding
#         new_embedding = (user_embedding + book_embedding) / 2
#         return new_embedding



# def generate_custom_recs(training_books, user_embedding, genre_weights, top_n=6):
#     books = list(books_collection.find({}))
#     print(f"Total books retrieved: {len(books)}")
#     update_book_embeddings(books)
#     # books_read = {book["book_id"] for book in retrieve_user_bookshelf(user_id)}
#     # books_to_read = {book["book_id"] for book in get_unread_books(user_id)}
#     book_embeddings = np.array([np.array(book["embedding"]) for book in books])

#     valid_books = books

#     # for book in books:
#     #     if book["_id"] not in books_read and book["_id"] not in books_to_read:
#     #         valid_books.append(book)

#     # # Debugging output
#     # print(
#     #     f"user_embedding shape: {user_embedding.shape if user_embedding is not None else 'None'}"
#     # )
#     # print(
#     #     f"book_embeddings shape: {book_embeddings.shape if book_embeddings is not None else 'None'}"
#     # )

#     # Check if user_embedding is None or empty
#     if user_embedding is None or user_embedding.size == 0:
#         print("Error: user_embedding is empty or None")
#         return []

#     # Ensure user_embedding is 2D
#     if user_embedding.ndim == 1:
#         user_embedding = user_embedding.reshape(1, -1)

#     # Check if book_embeddings is None or empty
#     if book_embeddings is None or book_embeddings.size == 0:
#         print("Error: book_embeddings is empty or None")
#         return []

#     # book_embeddings = np.array(book_embeddings, dtype=np.float64)  # Convert once after collecting

#     # Debugging output
#     # print(f"Number of books: {len(book_embeddings)}")
#     # print(f"First few book embeddings: {book_embeddings[:5] if len(book_embeddings) > 0 else 'No embeddings'}")

#     # similarities = cosine_similarity(user_embedding.reshape(1, -1), book_embeddings)[0]
#     # recommendations = [(book, sim) for book, sim in zip(books, similarities) if book["_id"] not in books_read]
#     # recommendations.sort(key=lambda x: x[1], reverse=True)

#     # return [book for book, _ in recommendations[:top_n]]
#     use_similarities = True
#     if np.all(user_embedding == 0):
#         use_similarities = False
#     similarities = cosine_similarity(user_embedding.reshape(1, -1), book_embeddings)[0]

#     recommendations = []
#     # print("genre_weights:", genre_weights)

#     if use_similarities:
#         for book, sim in zip(valid_books, similarities):
#             genre_score = sum(
#                 genre_weights.get(genre, 0) for genre in book.get("genre_tags", [])
#             )
#             total_score = sim + genre_score * 0.1  # Adjust weight factor as needed
#             recommendations.append((book, total_score))
#     else:
#         # print("No embedding, just genres.")
#         for book in valid_books:
#             book_genres = [g.lower() for g in book.get("genre_tags", [])]
#             genre_score = 0
#             for genre, weight in genre_weights.items():
#                 genre_lower = genre.lower()
#                 if any(genre_lower in book_genre for book_genre in book_genres):
#                     genre_score += weight
#             # print("GENRE TAGS:", book.get("genre_tags", []))
#             recommendations.append((book, genre_score))

#     recommendations.sort(key=lambda x: x[1], reverse=True)
#     book_scores = [score for _, score in recommendations[:5]]
#     print(book_scores)
#     best_books = [book for book, _ in recommendations[:2]]

#     # Create a list of books to filter for duplicates
#     start = 2
#     end = 40
#     remaining_books = [book for book, _ in recommendations[start:end]]

#     # Filter out books that are considered duplicates (same author and similar title)
#     # def adjustAuthor(author):
#     #     if isinstance(author, list):
#     #         author = " ".join(author)
#     #     author = author.lower()
#     #     author = re.sub(r"[^\w\s]", "", author)
#     #     words = author.split()
#     #     words.sort()
#     #     return " ".join(words)

#     # seen_authors = set()
#     filtered_books = []
#     for book in remaining_books:
#         raw_author = book.get("author", "")
#         #author = adjustAuthor(raw_author)
#         # print("AUTHOR: ", author)

#         # if author in seen_authors:
#         #     continue

#         duplicate_found = False
#         for seen_book in best_books:
#             if is_duplicate(book, seen_book):
#                 duplicate_found = True
#                 break
#         if not duplicate_found:
#             # seen_authors.add(author)
#             filtered_books.append(book)

#     # Ensure we have enough books to randomly select
#     num_needed = top_n - len(best_books)
#     if len(filtered_books) < num_needed:
#         random_books = filtered_books
#     else:
#         random_books = random.sample(filtered_books, num_needed)

#     # Combine the best 2 books with the randomly selected 4 books
#     final_recommendations = best_books + random_books

#     return final_recommendations



# def evaluate_predictions(user_id, test_books, recommendations):
#     test_embeddings = []
#     for book in test_books:
#         test_book = books_collection.find_one({"_id": book["book_id"]})
#         if test_book and "embedding" in test_book:
#             test_embeddings.append(test_book["embedding"])

#     rec_embeddings = [book["embedding"] for book in recommendations if "embedding" in book]

#     if test_embeddings and rec_embeddings:
#         test_matrix = np.array(test_embeddings)
#         rec_matrix = np.array(rec_embeddings)
#         similarity_matrix = cosine_similarity(rec_matrix, test_matrix)
#         avg_similarity = np.mean(similarity_matrix)
#         print(f"Average cosine similarity between recommendations and test books: {avg_similarity:.4f}")
#     else:
#         print("Insufficient embeddings for similarity analysis.")
    
#     print("TESTING BOOKS (what we want to match, other half of shelf)")
#     test_book_ids = {book["book_id"] for book in test_books}
#     for i in test_book_ids:
#         print(read_book_field(i, "title"))
#     # test_book = {book["title"] for book in test_books}
#     predicted_book_ids = {book["_id"] for book in recommendations}
#     predicted_book = {book["title"] for book in recommendations}
#     intersection = test_book_ids.intersection(predicted_book_ids)

#     print(f"User: {user_id}")
#     print(f"Total test books: {len(test_books)}")
#     # print(test_book)
#     print(f"Recommendations matched: {len(intersection)}")
#     print(predicted_book)
#     print(f"Matched Book IDs: {intersection}\n")
#     return len(intersection)


# def run_test(user_id):
#     training_books, test_books = split_user_bookshelf(user_id)
#     print("TRAINING DATA")
#     t_book_ids = {book["book_id"] for book in training_books}
#     for i in t_book_ids:
#         print(read_book_field(i, "title"))

#     if not training_books or not test_books:
#         print(f"NO DATA")
#         return

#     user_embedding, genre_weights = simulate_onboarding(user_id, training_books)
#     # print(user_embedding)
#     # print(genre_weights)
#     recommendations = generate_custom_recs(training_books, user_embedding, genre_weights)
#     evaluate_predictions(user_id, test_books, recommendations)


# if __name__ == "__main__":
#     run_test("67f69fb4d9f34beef0e5a301") # katelyns
    # run_test('67f81d0dfdf727a9cd85b45d') # anna

######## TEST SCRIPT PYTHON ##########
import random
import numpy as np
from database import collections
from models.books import books_collection, read_book_field
from recmodel import update_book_embeddings, is_duplicate, generate_recs
from sklearn.metrics.pairwise import cosine_similarity
from models.users import retrieve_genre_weights

def get_user_books(user_id):
    user_bookshelf_collection = collections["User_Bookshelf"]
    full_shelf = list(user_bookshelf_collection.find({"user_id": user_id}))
    return full_shelf

def evaluate_against_bookshelf(user_id, recommendations):
    bookshelf_books = get_user_books(user_id)
    shelf_embeddings = [books_collection.find_one({"_id": book["book_id"]})["embedding"]
                        for book in bookshelf_books
                        if books_collection.find_one({"_id": book["book_id"]}) and
                        "embedding" in books_collection.find_one({"_id": book["book_id"]})]
    rec_embeddings = [book["embedding"] for book in recommendations if "embedding" in book]
    if shelf_embeddings and rec_embeddings:
        shelf_matrix = np.array(shelf_embeddings)
        rec_matrix = np.array(rec_embeddings)
        similarity_matrix = cosine_similarity(rec_matrix, shelf_matrix)
        avg_similarity = np.mean(similarity_matrix)
        print(f"Average cosine similarity between recommendations and full bookshelf: {avg_similarity:.4f}")
    else:
        print("Insufficient embeddings for similarity analysis.")

def run_test(user_id):
    user_books = get_user_books(user_id)
    if not user_books:
        print("NO DATA")
        return
    recommendations = generate_recs(user_id=user_id, top_n=10)
    evaluate_against_bookshelf(user_id, recommendations)

if __name__ == "__main__":
    run_test("67f69fb4d9f34beef0e5a301")
    run_test('67f81d0dfdf727a9cd85b45d')