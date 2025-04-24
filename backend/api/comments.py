from flask import Blueprint, request, jsonify
from flask_cors import CORS
from models.comments import (
    create_initial_comment,
    get_all_comments_for_post,
    read_comment,
    reply_to_comment,
)

comments_bp = Blueprint("comments", __name__)
CORS(comments_bp)


# CREATE: Add a top-level comment to a post
@comments_bp.route("/<post_id>/comments", methods=["POST"])
def add_comment_to_post(post_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        comment_text = data.get("comment_text")

        if not all([user_id, comment_text]):
            return jsonify({"error": "Missing user_id or comment_text"}), 400

        result = create_initial_comment(post_id, user_id, comment_text)
        if "Error" in result:
            return jsonify({"error": result}), 400
        return jsonify({"message": "Comment created", "comment_id": str(result)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# CREATE: Reply to a comment
@comments_bp.route("/<post_id>/comments/<parent_comment_id>/reply", methods=["POST"])
def reply_to_existing_comment(post_id, parent_comment_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        comment_text = data.get("comment_text")

        if not all([user_id, comment_text]):
            return jsonify({"error": "Missing user_id or comment_text"}), 400

        result = reply_to_comment(post_id, user_id, comment_text, parent_comment_id)
        if "Error" in result:
            return jsonify({"error": result}), 400
        return jsonify({"message": "Reply created", "comment_id": str(result)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# READ: Get all comments for a post
@comments_bp.route("/<post_id>/comments", methods=["GET"])
def get_comments_for_post(post_id):
    try:
        result = get_all_comments_for_post(post_id)
        if isinstance(result, list):
            return jsonify(result), 200
        return jsonify({"error": result}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# READ: Get a single comment
@comments_bp.route("/<post_id>/comments/<comment_id>", methods=["GET"])
def get_single_comment(post_id, comment_id):
    try:
        result = read_comment(comment_id)
        if isinstance(result, dict):
            return jsonify(result), 200
        return jsonify({"error": result}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# # UPDATE: Update a comment's text
# @comments_bp.route("/<post_id>/comments/<comment_id>", methods=["PUT"])
# def update_existing_comment(post_id, comment_id):
#     try:
#         data = request.get_json()
#         comment_text = data.get("comment_text")

#         if not comment_text:
#             return jsonify({"error": "Missing comment_text"}), 400

#         result = update_comment(comment_id, comment_text)
#         if result == "Comment updated successfully.":
#             return jsonify({"message": result}), 200
#         return jsonify({"error": result}), 404

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# # DELETE: Delete a comment
# @comments_bp.route("/<post_id>/comments/<comment_id>", methods=["DELETE"])
# def delete_existing_comment(post_id, comment_id):
#     try:
#         data = request.get_json(silent=True) or {}
#         user_id = data.get("user_id") or request.args.get("user_id")

#         if not user_id:
#             return jsonify({"error": "Missing user_id"}), 400

#         comment = read_comment(comment_id)
#         if isinstance(comment, str):
#             return jsonify({"error": comment}), 404

#         if str(comment["user_id"]) != user_id:
#             return jsonify({"error": "Unauthorized"}), 403

#         result = delete_comment(comment_id)
#         return jsonify({"message": result}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
