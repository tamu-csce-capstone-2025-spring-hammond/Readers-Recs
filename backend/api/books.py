from flask import Blueprint, request, jsonify
from flask_cors import CORS
from database import collections
from schemas import BookSchema
from bson import ObjectId

books_bp = Blueprint("books", __name__)
CORS(books_bp)

@books_bp.route("/books", methods=["GET"])
def search_books():
    """
    Search for books in the database.
    
    - `query`: The search term (Required).
    - `type`: Search by "title", "author", "isbn", or "any" (Optional, default: "any").
    """
    query = request.args.get("query", "").strip()
    search_type = request.args.get("type", "any").lower()

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    filters = []
    search_term = query.lower()

    if search_type in ["title", "any"]:
        filters.append({"title": {"$regex": search_term, "$options": "i"}})
    if search_type in ["author", "any"]:
        filters.append({"author": {"$regex": search_term, "$options": "i"}})
    if search_type in ["isbn", "any"]:
        filters.append({"isbn": {"$regex": search_term, "$options": "i"}})
    
    query_filter = {"$or": filters} if filters else {}

    books_cursor = collections["Books"].find(query_filter).limit(50)
    books = [
        {**book, "_id": str(book["_id"])} for book in books_cursor
    ]

    if not books:
        return jsonify({"error": "No books found"}), 404

    return jsonify(books), 200
