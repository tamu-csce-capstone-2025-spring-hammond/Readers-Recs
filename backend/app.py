# backend/app.py
from backend.models.books import read_book_by_identifier
from backend.database import collections, db, close_connection


def main():
    print("Starting the application...")

    print("Available collections:")
    for name in collections.keys():
        print(f"- {name}")

    print("Collections in the database:", db.list_collection_names())

    run_application_logic()

    print("Closing the application.")
    close_connection()


def run_application_logic():
    # Application logic goes here
    print("Running application logic.")
    print(read_book_by_identifier("517149257", "isbn"))


if __name__ == "__main__":
    main()
