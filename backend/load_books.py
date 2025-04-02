from datetime import datetime
import json
import os
import threading
import time
from bson import ObjectId
from models.books import books_collection  # Import your MongoDB collection

class BookCollection:
    def __init__(self, cache_file="books_cache.json"):
        """
        Initializes the BookCollection and starts a background thread to refresh books.
        :param refresh_interval: Time in seconds before refreshing (default: 24 hours)
        """
        self.books = []
        self.lock = threading.Lock()
        self.cache_file = cache_file

        # Load books from cache or database
        self.load_books()

        # Start background refresh thread

    def load_books(self):
        """Loads books from JSON cache file if available, otherwise fetches from MongoDB."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cached_books = json.load(f)
            
            # Convert _id from string back to ObjectId
            self.books = [
                {**book, 
                 "_id": ObjectId(book["_id"]),
                 "publication_date": datetime.fromisoformat(book["publication_date"]),
                } for book in cached_books
            ]
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Loaded {len(self.books)} books from cache.")
        else:
            self.refresh_books()

    def refresh_books(self):
        """Fetches all books from MongoDB and updates the cache file."""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Refreshing book collection...")

        start_time = time.time()
        new_books = list(books_collection.find({}).limit(10000))

        # Convert ObjectId to string before saving
        books_to_cache = [
            {
                **book, 
                "_id": str(book["_id"]),
                "publication_date": book["publication_date"].isoformat() if book.get("publication_date") else "2000-01-01",

            } for book in new_books
        ]

        with self.lock:
            self.books = new_books

        # Save to JSON cache file
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(books_to_cache, f, indent=4)  # Pretty print for readability

        elapsed_time = time.time() - start_time
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Book collection updated ({len(new_books)} books) in {elapsed_time:.4f} seconds.")

    def _refresh_loop(self):
        """Runs a loop to refresh the book collection every 24 hours."""
        while True:
            time.sleep(self.refresh_interval)
            self.refresh_books()

    def get_books(self):
        """Returns all books from memory."""
        with self.lock:
            return self.books.copy()  # Return a copy to prevent modifications
        

# books = BookCollection()

