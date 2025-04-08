from flask import Flask, request
from flask_cors import CORS
from api.books import books_bp
from api.user import user_bp
from api.bookshelf import shelf_bp
from api.recommendations import recommendation_bp
from api.posts import discussion_bp
from api.comments import comments_bp
from api.chat_messages import chat_bp
import os 

app = Flask(__name__)

# Enable CORS for specific origins and handle OPTIONS requests
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000", 
                "https://*.vercel.app",
                "https://readers-recs-backend.onrender.com"
            ],
            "supports_credentials": True
        }
    },
)


# Register API Blueprints
app.register_blueprint(books_bp, url_prefix="/api")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(shelf_bp, url_prefix="/shelf")
app.register_blueprint(recommendation_bp, url_prefix="/recs")
app.register_blueprint(discussion_bp, url_prefix="/api/books")
app.register_blueprint(comments_bp, url_prefix="/api/posts")
app.register_blueprint(chat_bp, url_prefix="/api/chat")


# Explicit handling for preflight OPTIONS requests
@app.before_request
def before_request():
    if request.method == "OPTIONS":
        return "", 200  # Respond with HTTP 200 for OPTIONS requests


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)