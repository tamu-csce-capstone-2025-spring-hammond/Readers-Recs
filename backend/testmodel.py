import random
import numpy as np
# from models.user_bookshelf import retrieve_user_bookshelf
from database import collections
# from schemas import UserBookshelfSchema 
from models.books import books_collection, read_book_field
from recmodel import update_book_embeddings, is_duplicate
from sklearn.metrics.pairwise import cosine_similarity
from models.users import retrieve_genre_weights, users_collection


def split_user_bookshelf(user_id):
    user_bookshelf_collection = collections["User_Bookshelf"]
    full_shelf = list(user_bookshelf_collection.find({"user_id": user_id}))
    print(len(full_shelf))
    valid_books = [book for book in full_shelf if book["status"] in ["read", "currently-reading", "to-read"]]

    if len(valid_books) < 2:
        print(f"User {user_id} does not have enough valid books to split.")
        return [], []

    random.shuffle(valid_books)
    midpoint = len(valid_books) // 2
    return valid_books[:midpoint], valid_books[midpoint:]


def simulate_onboarding(user_id, training_books):
    genre_weights = retrieve_genre_weights(user_id)
    user_embedding = np.zeros(384)
    book_objs = []

    for book_entry in training_books:
        rating = book_entry.get("rating", "")
        if not rating:
            continue

        book = books_collection.find_one({"_id": book_entry["book_id"]})
        if not book:
            continue

        if rating not in ["pos", "neg", "mid"]:
            continue

        # Update genre weights
        genres = book.get("genre_tags", [])
        weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0
        for genre in genres:
            genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

        # Update user embedding for positive ratings
        if rating == "pos" and "embedding" in book and book["embedding"]:
            user_embedding += np.array(book["embedding"])
            book_objs.append(book)

    # Finalize embedding
    if book_objs:
        user_embedding /= len(book_objs)

    return user_embedding, genre_weights

def process_user_rating(user_embed, user_genweight, book_id, rating):
    """Handles user book interactions and updates preferences."""
    if not rating:
        print("Book read but not rated by user.")
        return
    if rating not in ["pos", "neg", "mid"]:
        print("Invalid rating.")
        return

    # Fetch or create user
    # user = read_user(user_id)
    # if not user:
    #     print("USER NOT FOUND")

    book = books_collection.find_one({"_id": book_id})
    if not book:
        print(f"Book {book_id} not found in database.")
        return

    # Genre weight update
    genres = book.get("genre_tags", [])
    weight_change = 1 if rating == "pos" else -1 if rating == "neg" else 0

    genre_weights = user_genweight
    if isinstance(genre_weights, str):
        genre_weights = {}  # Initialize if not found

    for genre in genres:
        genre_weights[genre] = genre_weights.get(genre, 0) + weight_change

    # print(update_user_gw(user_id, genre_weights))
    # print("User new genre weights:", retrieve_genre_weights(user_id))
    # update_genre_weights(user_id, genre_weights)
    # Embedding update
    if rating == "pos":
        user_embedding = user_embed  # Retrieve embedding from DB
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
        return new_embedding



def generate_custom_recs(training_books, user_embedding, genre_weights, top_n=6):
    books = list(books_collection.find({}))
    print(f"Total books retrieved: {len(books)}")
    update_book_embeddings(books)
    #book_embeddings = np.array([np.array(book["embedding"]) for book in books])
    book_embeddings = []
    valid_books = []

    for book in books:
        emb = book.get("embedding")
        if isinstance(emb, list) and len(emb) == 384:
            try:
                vec = np.array(emb, dtype=np.float64)
                book_embeddings.append(vec)
                valid_books.append(book)
            except Exception as e:
                print(f"Skipping book {book['_id']} due to bad embedding: {e}")
        else:
            print(f"Skipping book {book['_id']}: Invalid embedding shape/type.")
            
    book_embeddings = np.stack(book_embeddings) if book_embeddings else np.zeros((1, 384))
    

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


    # return [book for book, _ in recommendations[:top_n]]
    use_similarities = True
    if np.all(user_embedding == 0):
        use_similarities = False
    similarities = cosine_similarity(user_embedding.reshape(1, -1), book_embeddings)[0]

    recommendations = []
    # print("genre_weights:", genre_weights)

    if use_similarities:
        for book, sim in zip(valid_books, similarities):
            # print("GENRE WEIGHTS:", genre_weights)
            genre_score = sum(
                genre_weights.get(genre, 0) for genre in book.get("genre_tags", [])
            )
            total_score = sim + genre_score   # Adjust weight factor as needed
            recommendations.append((book, total_score))
            # recommendations.append((book, sim))
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
    start = 2
    end = 40
    remaining_books = [book for book, _ in recommendations[start:end]]

    # Filter out books that are considered duplicates (same author and similar title)
    # def adjustAuthor(author):
    #     if isinstance(author, list):
    #         author = " ".join(author)
    #     author = author.lower()
    #     author = re.sub(r"[^\w\s]", "", author)
    #     words = author.split()
    #     words.sort()
    #     return " ".join(words)

    # seen_authors = set()
    filtered_books = []
    for book in remaining_books:
        raw_author = book.get("author", "")
        #author = adjustAuthor(raw_author)
        # print("AUTHOR: ", author)

        # if author in seen_authors:
        #     continue

        duplicate_found = False
        for seen_book in best_books:
            if is_duplicate(book, seen_book):
                duplicate_found = True
                break
        if not duplicate_found:
            # seen_authors.add(author)
            filtered_books.append(book)

    # Ensure we have enough books to randomly select
    num_needed = top_n - len(best_books)
    if len(filtered_books) < num_needed:
        random_books = filtered_books
    else:
        random_books = random.sample(filtered_books, num_needed)

    # Combine the best 2 books with the randomly selected 4 books
    final_recommendations = best_books + random_books

    return final_recommendations

def genre_coverage_score(genre_weights, recommendations):
    if not genre_weights or not recommendations:
        return 0.0

    max_weight = max(genre_weights.values()) if genre_weights else 1
    max_tags_per_book = max(len(book.get("genre_tags", [])) for book in recommendations) or 1
    max_possible_score_per_book = max_weight * max_tags_per_book

    total_score = 0
    count = 0

    for book in recommendations:
        genres = book.get("genre_tags", [])
        score = sum(genre_weights.get(genre, 0) for genre in genres)
        total_score += score
        count += 1

    raw_average_score = total_score / count if count else 0.0
    normalized_score = raw_average_score / max_possible_score_per_book if max_possible_score_per_book else 0.0

    return normalized_score

def evaluate_predictions(user_id, train_books, test_books, recommendations, genre_weights):
    train_embeddings = []
    for book in train_books:
        train_book = books_collection.find_one({"_id": book["book_id"]})
        if train_book and "embedding" in train_book:
            train_embeddings.append(train_book["embedding"])

    test_embeddings = []
    for book in test_books:
        test_book = books_collection.find_one({"_id": book["book_id"]})
        if test_book and "embedding" in test_book:
            test_embeddings.append(test_book["embedding"])

    rec_embeddings = [book["embedding"] for book in recommendations if "embedding" in book]

    test_embeddings = []
    for book in test_books:
        test_book = books_collection.find_one({"_id": book["book_id"]})
        if test_book and "embedding" in test_book:
            test_embeddings.append(test_book["embedding"])

    rec_embeddings = [book["embedding"] for book in recommendations if "embedding" in book]
    
    sim_traintest_mean = None
    sim_trainrec_mean = None
    output_lines = []
    
    if train_embeddings and test_embeddings:
        sim_traintest = cosine_similarity(np.array(train_embeddings), np.array(test_embeddings))
        sim_traintest_mean = np.mean(sim_traintest)
        print(f"Avg cosine similarity (train vs test): {np.mean(sim_traintest):.4f}")

    if train_embeddings and rec_embeddings:
        sim_trainrec = cosine_similarity(np.array(rec_embeddings), np.array(train_embeddings))
        sim_trainrec_mean = np.mean(sim_trainrec)
        print(f"Avg cosine similarity (train vs recs): {np.mean(sim_trainrec):.4f}")
        
    if sim_traintest_mean and sim_trainrec_mean:
        ratio = sim_trainrec_mean / sim_traintest_mean if sim_traintest_mean != 0 else float('inf')
        print(f"Ratio (train vs recs) / (train vs test): {ratio:.4f}")
    
    # embedding_score = embedding_coverage_score(test_books, recommendations)
    # print(f"Embedding Coverage Score: {embedding_score:.4f}")
    genre_score = genre_coverage_score(genre_weights, recommendations)
    print(f"Genre Coverage Score: {genre_score:.4f}")

    
    output_lines.append(f"User: {user_id}")
    output_lines.append(f"Total training books: {len(train_books)}")
    output_lines.append(f"Total test books: {len(test_books)}")
    output_lines.append(f"Genre Coverage Score: {genre_score}")
    # output_lines.append(f"Avg cosine similarity (train vs test): {np.mean(sim_traintest):.4f}")
    # output_lines.append(f"Avg cosine similarity (train vs recs): {np.mean(sim_trainrec):.4f}")
    # output_lines.append(f"Ratio (train vs recs) / (train vs test): {ratio:.4f}")
    
    
    
    with open(f"genre_similarity_logs/{user_id}.txt", "w") as f:
        for line in output_lines:
            print(line)
            f.write(line + "\n")
               
    return genre_score

    # if test_embeddings and rec_embeddings:
    #     test_matrix = np.array(test_embeddings)
    #     rec_matrix = np.array(rec_embeddings)
    #     similarity_matrix = cosine_similarity(rec_matrix, test_matrix)
    #     avg_similarity = np.mean(similarity_matrix)
    #     print(f"Average cosine similarity between recommendations and test books: {avg_similarity:.4f}")
    # else:
    #     print("Insufficient embeddings for similarity analysis.")
    
    # print("TESTING BOOKS (what we want to match, other half of shelf)")
    # test_book_ids = {book["book_id"] for book in test_books}
    # for i in test_book_ids:
    #     print(read_book_field(i, "title"))
    # # test_book = {book["title"] for book in test_books}
    # predicted_book_ids = {book["_id"] for book in recommendations}
    # predicted_book = {book["title"] for book in recommendations}
    # intersection = test_book_ids.intersection(predicted_book_ids)

    # print(f"User: {user_id}")
    # print(f"Total test books: {len(test_books)}")
    # # print(test_book)
    # print(f"Recommendations matched: {len(intersection)}")
    # print(predicted_book)
    # print(f"Matched Book IDs: {intersection}\n")
    # return ratio


def run_test(user_id):
    training_books, test_books = split_user_bookshelf(user_id)
    # print("TRAINING DATA")
    # t_book_ids = {book["book_id"] for book in training_books}
    # for i in t_book_ids:
    #     print(read_book_field(i, "title"))

    if not training_books or not test_books:
        print(f"NO DATA")
        return None

    user_embedding, genre_weights = simulate_onboarding(user_id, training_books)
    # print(user_embedding)
    # print(genre_weights)
    recommendations = generate_custom_recs(training_books, user_embedding, genre_weights)
    return evaluate_predictions(user_id, training_books, test_books, recommendations, genre_weights)


if __name__ == "__main__":
    # users_collection = collections["Users"]
    import os
    os.makedirs("genre_similarity_logs", exist_ok=True)
    users = list(users_collection.find({}))
    ucount = 0
    rsum = 0
    for user in users:
        path = f"genre_similarity_logs/{user['_id']}.txt"
        if os.path.exists(path):
            print(f"Skipping user {user['_id']} (log already exists)")
            continue

        ratio = run_test(user["_id"])
        if ratio is not None:
            rsum += ratio
            ucount += 1
    print("TOTAL RSUM: ", rsum)
    print("\n")
    print("USER COUNT: ", ucount)
    print("\n")
    print("AVERAGE GENRE SCORE RATIO: ", rsum/ucount)
    
        
    # run_test("67f69fb4d9f34beef0e5a301") # katelyns
    # run_test('67f81d0dfdf727a9cd85b45d') # anna
