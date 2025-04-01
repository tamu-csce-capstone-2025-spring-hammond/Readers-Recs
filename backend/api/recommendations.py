from models.books import read_book_by_bookId
from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from recmodel import recommend_books
from bson import ObjectId


recommendation_bp = Blueprint("recommendation", __name__)
CORS(recommendation_bp)


def objectid_to_str(obj):
    """Helper function to convert ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not ObjectId")



@recommendation_bp.route("/api/user/<user_id>/recommendations", methods=["GET"])
def get_book_recommendations(user_id):
    """
    API endpoint to get book recommendations for a user.
    """
    try:
        recommendations = recommend_books(user_id)
        if recommendations:
            for book in recommendations:
                book["_id"] = objectid_to_str(book["_id"])
        return jsonify({"user_id": user_id, "recommendations": recommendations}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500