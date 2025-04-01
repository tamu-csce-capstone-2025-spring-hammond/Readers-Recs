from flask import Blueprint, request, jsonify
from flask_cors import CORS

# from database import collections
# from bson import ObjectId
import requests

from backend.models.users import create_user, read_user_by_email

user_bp = Blueprint("user", __name__)
CORS(user_bp)


@user_bp.route("/profile", methods=["GET"])
def get_user_profile():
    """
    Retrieve user profile information.

    Requires an Authorization header with a Bearer token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    access_token = auth_header.split(" ")[1]

    # Verify token with Google OAuth
    token_info_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={access_token}"
    token_info_response = requests.get(token_info_url)
    token_info = token_info_response.json()

    if "email" not in token_info:
        return token_info_response.json()

    # Fetch user data from database
    user = read_user_by_email(email=token_info["email"])
    if not user:
        return jsonify({f'"error": "{token_info}"'}), 404

    if isinstance(user, str):  # User not found, create a new user
        # Create user from Google profile data
        new_user_data = {
            "first_name": token_info.get("given_name", ""),
            "last_name": token_info.get("family_name", ""),
            "username": token_info["email"].split("@")[
                0
            ],  # You can use the email or generate a unique username
            "email_address": token_info["email"],
            "oauth": {
                "access_token": access_token,
                # Add additional OAuth details if necessary
            },
            "profile_image": token_info.get("picture", ""),
            "interests": [],  # You can add default interests or leave it empty
            "demographics": {},  # You can fill in demographics data or leave it empty
        }

        # Create new user in the database
        new_user_id = create_user(**new_user_data)
        if new_user_id.startswith("Error"):
            print("error:", new_user_id)
            return jsonify({"error": new_user_id}), 500

        # After user creation, fetch the newly created user to return the profile
        user = read_user_by_email(token_info["email"])

    # Check if user is found and return profile
    if isinstance(user, str):
        return (
            jsonify({"error": user}),
            404,
        )  # If user creation failed or user not found

    # Access user attributes properly
    user_profile = {
        "id": str(user["_id"]),  # Ensure _id is converted to string
        "name": f"{user.get('first_name', '')} {user.get('last_name', '')}",  # Combine first and last name
        "email": user.get("email_address", ""),
        "profile_picture": user.get("profile_image", ""),
        "created_at": user.get("created_at", ""),
    }

    return jsonify(user_profile), 200
