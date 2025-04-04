from flask import Blueprint, request, jsonify
from flask_cors import CORS
from models.posts import (
    create_post,
    read_post,
    get_all_posts_for_book,
    update_post,
    delete_post,
)
from bson import ObjectId

discussion_bp = Blueprint("posts", __name__)
CORS(discussion_bp)


@discussion_bp.route("/<book_id>/posts", methods=["POST"])
def create_discussion_post(book_id):
    """
    Create a discussion post for a specific book.
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        title = data.get("title")
        post_text = data.get("post_text")
        tags = data.get("tags", [])

        if not all([user_id, title, post_text]):
            return jsonify({"error": "Missing required fields"}), 400

        result = create_post(user_id, book_id, title, post_text, tags)

        if "Error" in result:
            return jsonify({"error": result}), 400
        else:
            return jsonify({"message": "Post created", "post_id": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def convert_objectid(doc):
    if isinstance(doc, list):
        return [convert_objectid(item) for item in doc]
    if isinstance(doc, dict):
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items()}
    return doc

@discussion_bp.route("/<book_id>/posts", methods=["GET"])
def get_all_discussion_posts(book_id):
    try:
        result = get_all_posts_for_book(book_id)
        if isinstance(result, list):
            result = convert_objectid(result)   # 👈 ADD THIS
            return jsonify(result), 200
        else:
            return jsonify({"error": result}), 400
    except Exception as e:
        print("Error fetching posts:", str(e))
        return jsonify({"error": str(e)}), 500


@discussion_bp.route("/<book_id>/posts/<post_id>", methods=["PUT"])
def update_discussion_post(post_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        title = data.get("title", "")
        post_text = data.get("post_text", "")
        tags = data.get("tags")

        post = read_post(post_id)
        if isinstance(post, str):  # Error message
            return jsonify({"error": post}), 404

        if str(post["user_id"]) != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        result = update_post(post_id, title=title, post_text=post_text, tags=tags)
        return jsonify({"message": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@discussion_bp.route("/<book_id>/posts/<post_id>", methods=["DELETE"])
def delete_discussion_post(post_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        post = read_post(post_id)
        if isinstance(post, str):
            return jsonify({"error": post}), 404

        if str(post["user_id"]) != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        result = delete_post(post_id)
        return jsonify({"message": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500