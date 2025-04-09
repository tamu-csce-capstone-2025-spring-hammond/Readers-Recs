from flask import Blueprint, request, jsonify
from flask_cors import CORS

# from database import collections
# from bson import ObjectId
import requests

from models.users import (
    create_user,
    read_user_by_email,
    update_user_settings,
    read_user_by_username,
)

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
        "username": user.get("username", ""),
    }

    return jsonify(user_profile), 200


@user_bp.route("/profile/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    """
    Fetch a user's profile by user_id (NOT by access token).
    """
    from backend.models.users import read_user_by_id

    user = read_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return (
        jsonify(
            {
                "id": str(user["_id"]),
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                "profile_picture": user.get("profile_image", ""),
            }
        ),
        200,
    )


@user_bp.route("/profile/<user_id>/edit-profile", methods=["POST"])
def edit_profile(user_id):
    try:
        data = request.get_json()

        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        username = data.get("username", "")
        profile_image = data.get("profile_image", "")

        # if there is a username, validate that it is unique
        if username:
            existing_user = read_user_by_username(username)
            if existing_user and str(existing_user["_id"]) != user_id:
                return jsonify({"error": "Username already exists."}), 400
            if existing_user and str(existing_user["_id"]) == user_id:
                existing_user = None

        result = update_user_settings(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            profile_image=profile_image,
        )

        if result.startswith("Error"):
            return jsonify({"error": result}), 400

        return jsonify({"message": "Profile updated successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/check-email-exists", methods=["GET"])
def check_email_exists():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    user = read_user_by_email(email)

    # print("DEBUG: Queried Email:", email)
    # print("DEBUG: User Found:", user)
    exists = False if user == "User not found." or user is None else True
    return jsonify({"exists": exists})
