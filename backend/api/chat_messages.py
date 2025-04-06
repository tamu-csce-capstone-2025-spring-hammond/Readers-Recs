from flask import Blueprint, request, jsonify
from database import collections
from models.chat_messages import create_chat_message, get_all_chat_messages_for_book
from bson import ObjectId
from models.books import read_book_by_bookId
from models.user_bookshelf import get_read_books

chat_bp = Blueprint("chat", __name__)

users_collection = collections["Users"]
chat_messages_collection = collections["Chat_Messages"]


# GET: Get all chat messages for a book
@chat_bp.route("/<book_id>/messages", methods=["GET"])
def get_chat_messages_for_book(book_id):
    try:
        msgs = get_all_chat_messages_for_book(book_id)
        if not isinstance(msgs, list):
            return jsonify({"error": msgs}), 400
        return jsonify(msgs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# POST: Send a new chat message
@chat_bp.route("/<book_id>/send", methods=["POST"])
def send_chat_message(book_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        message_text = data.get("message_text")

        if not all([user_id, message_text]):
            return jsonify({"error": "Missing user_id or message_text"}), 400

        result = create_chat_message(book_id, user_id, message_text)
        if "Error" in result:
            return jsonify({"error": result}), 400

        return jsonify({"message": "Message sent", "message_id": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET: Get the last read book for a user with more information than the similar user API function
@chat_bp.route("/user/<user_id>/lastread", methods=["GET"])
def get_chat_last_read_book(user_id):
    try:
        books = get_read_books(user_id)
        if isinstance(books, str):
            return jsonify({"error": books}), 400

        books_with_finish_date = [
            book for book in books if book.get("date_finished") is not None
        ]

        books_with_finish_date.sort(
            key=lambda x: x.get("date_finished", ""), reverse=True
        )

        if books_with_finish_date:
            last_read = books_with_finish_date[0]
            rating = last_read.get("rating", "mid")

            b = read_book_by_bookId(last_read["book_id"])
            if isinstance(b, str):
                return jsonify({"error": b}), 404

            b["rating"] = rating
            b["date_finished"] = last_read["date_finished"]

            for k, v in list(b.items()):
                if isinstance(v, ObjectId):
                    b[k] = str(v)

            return jsonify(b), 200
        else:
            return jsonify({"message": "No books marked as read yet."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UPDATE: Update a chat message
@chat_bp.route("/<book_id>/update/<message_id>", methods=["PUT"])
def update_chat_message_api(book_id, message_id):
    try:
        data = request.get_json()
        message_text = data.get("message_text")

        if not message_text:
            return jsonify({"error": "Missing message_text"}), 400

        result = update_chat_message(message_id, message_text)
        if isinstance(result, str) and "Error" in result:
            return jsonify({"error": result}), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE: Delete a chat message
@chat_bp.route("/<book_id>/delete/<message_id>", methods=["DELETE"])
def delete_chat_message_api(book_id, message_id):
    try:
        result = delete_chat_message(message_id)
        if isinstance(result, str) and "Error" in result:
            return jsonify({"error": result}), 400

        return jsonify({"message": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
