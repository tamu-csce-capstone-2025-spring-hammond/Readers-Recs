from flask import Blueprint, jsonify, request
from flask_cors import CORS
from recmodel import onboarding_recommendations, recommend_books
from bson import ObjectId
import requests

from models.users import read_user_by_email


recommendation_bp = Blueprint("recommendation", __name__)
CORS(recommendation_bp)


def objectid_to_str(obj):
    """Helper function to convert ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)


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
    
@recommendation_bp.route("/api/user/onboarding/recommendations", methods=["POST"])
def get_onboarding_recommendations():
    """
    API endpoint to get book recommendations for a user during onboarding.
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        access_token = auth_header.split(" ")[1]

        token_info_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={access_token}"
        token_info_response = requests.get(token_info_url)
        token_info = token_info_response.json()

        if "email" not in token_info:
            return jsonify({"error": "Invalid token"}), 401

        user = read_user_by_email(token_info["email"])
        if not user or isinstance(user, str):
            return jsonify({"error": "User not found"}), 404

        print("USER:", user)
        user_id = user["_id"]
        print("API ENDPOINT USER ID:", user_id)
        data = request.get_json()
        init_genres = data["genres"]
        print("init_genres:", init_genres)
        result = onboarding_recommendations(user_id, init_genres)
        if result:
            return jsonify({ "genres_updated": result}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
