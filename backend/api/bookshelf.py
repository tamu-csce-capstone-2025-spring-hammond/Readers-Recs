from datetime import datetime
from backend.models.books import read_book_by_bookId
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from bson import ObjectId

from backend.models.user_bookshelf import (
    create_user_bookshelf,
    delete_user_bookshelf,
    get_currently_reading_books,
    get_read_books,
    get_unread_books,
    rate_book,
    update_user_bookshelf_status,
)

shelf_bp = Blueprint("shelf", __name__)
CORS(shelf_bp)


def objectid_to_str(obj):
    """Helper function to convert ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not ObjectId")


@shelf_bp.route("/api/user/<user_id>/books/lastread", methods=["GET"])
def get_last_read_book(user_id):
    """
    Get the last book finished (marked as "read") in the user's bookshelf.
    """
    try:
        books = get_read_books(user_id)
        if isinstance(books, list):
            # Filter books that have a date_finished
            books_with_finish_date = [
                book for book in books if book.get("date_finished") is not None
            ]

            # Sort books by date_finished in descending order (most recent first)
            books_with_finish_date.sort(key=lambda x: x["date_finished"], reverse=True)

            if books_with_finish_date:
                # Get the most recent book
                last_read_book = books_with_finish_date[0]

                # Fetch the full book details
                b = read_book_by_bookId(last_read_book["book_id"])
                b = {
                    key: (
                        objectid_to_str(value) if isinstance(value, ObjectId) else value
                    )
                    for key, value in b.items()
                }

                return jsonify(b), 200
            else:
                return jsonify({"message": "No books finished yet."}), 404
        else:
            return jsonify({"error": books}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@shelf_bp.route("/api/user/<user_id>/books/read", methods=["GET"])
def get_read_books_api(user_id):
    """
    Get all books marked as "read" in the user's bookshelf.
    """
    try:
        books = get_read_books(user_id)
        if isinstance(books, list):
            books_read = list()
            for book in books:
                b = read_book_by_bookId(book["book_id"])
                b = {
                    key: (
                        objectid_to_str(value) if isinstance(value, ObjectId) else value
                    )
                    for key, value in b.items()
                }
                books_read.append(b)
            return jsonify(books_read), 200
        else:
            return jsonify({"error": books}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@shelf_bp.route("/api/user/<user_id>/books/to-read", methods=["GET"])
def get_unread_books_api(user_id):
    """
    Get all books marked as "to read" in the user's bookshelf.
    """
    try:
        books = get_unread_books(user_id)
        if isinstance(books, list):
            books_to_read = list()
            for book in books:
                b = read_book_by_bookId(book["book_id"])
                b = {
                    key: (
                        objectid_to_str(value) if isinstance(value, ObjectId) else value
                    )
                    for key, value in b.items()
                }
                books_to_read.append(b)
            return jsonify(books_to_read), 200
        else:
            return jsonify({"error": books}), 400
    except Exception as e:

        return jsonify({"error": str(e)}), 500


@shelf_bp.route("/api/user/<user_id>/books/currently-reading", methods=["GET"])
def get_currently_reading_books_api(user_id):
    """
    Get all books marked as "currently reading" in the user's bookshelf.
    """
    try:
        books = get_currently_reading_books(user_id)
        if books:
            book = read_book_by_bookId(books[0]["book_id"])
            book = {
                key: objectid_to_str(value) if isinstance(value, ObjectId) else value
                for key, value in book.items()
            }
            return jsonify(book), 200

        else:
            print(books)
            return jsonify({"error": "No books currently reading."}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@shelf_bp.route("/api/user/<user_id>/bookshelf", methods=["POST"])
def add_book_to_bookshelf(user_id):
    """
    Add a new book to the user's bookshelf.
    """
    try:
        data = request.get_json()
        book_id = data["book_id"]
        status = data["status"]
        date_finished = None
        date_started = None
        current_date = datetime.now().date().isoformat()  # "YYYY-MM-DD"
        if status == "read":
            date_finished = current_date
        else:
            date_started = current_date

        if status == "currently-reading":
            books = get_currently_reading_books(user_id)
            if books:
                print(books[0]["book_id"])
                print(delete_user_bookshelf(user_id, books[0]["book_id"]))

        result = create_user_bookshelf(
            user_id=user_id,
            book_id=ObjectId(book_id),
            status=status,
            date_started=date_started,
            date_finished=date_finished,
        )

        if "Error" not in result:
            print("result:", result)
            return jsonify({"message": "Book added to bookshelf", "id": result}), 201
        else:
            print(result)
            return jsonify({"error": result}), 400

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


####### THESE API FUNCTIONS ARE UNUSED SO FAR
@shelf_bp.route("/api/user/<user_id>/bookshelf/<book_id>/status", methods=["PUT"])
def update_bookshelf_status(user_id, book_id):
    """
    Update the status of a book on the user's bookshelf.
    """
    try:
        data = request.get_json()
        new_status = data.get("status")
        date_finished = None
        date_started = None
        if new_status == "read":
            date_finished = datetime.now().date()
        else:
            date_started = datetime.now().date()

        result = update_user_bookshelf_status(
            user_id,
            book_id,
            new_status,
            date_finished=date_finished,
            date_started=date_started,
        )

        if "Error" not in result:
            return jsonify({"message": "Book status updated."}), 200
        else:
            return jsonify({"error": result}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@shelf_bp.route("/api/user/<user_id>/bookshelf/<book_id>/rating", methods=["PUT"])
def rate_book_api(user_id, book_id):
    """
    Rate a book in the user's bookshelf.
    """
    try:
        data = request.get_json()
        new_rating = data.get("rating")

        result = rate_book(user_id, book_id, new_rating)

        if "Error" not in result:
            return jsonify({"message": "Book rating updated."}), 200
        else:
            return jsonify({"error": result}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@shelf_bp.route("/api/user/<user_id>/bookshelf/<book_id>", methods=["DELETE"])
def delete_book_from_bookshelf(user_id, book_id):
    """
    Delete a book from the user's bookshelf.
    """
    try:
        result = delete_user_bookshelf(user_id, book_id)

        if "Error" not in result:
            return jsonify({"message": "Book deleted from bookshelf."}), 200
        else:
            return jsonify({"error": result}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
