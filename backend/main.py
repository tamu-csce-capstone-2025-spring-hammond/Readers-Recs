from flask import Flask, request
from flask_cors import CORS
from api.books import books_bp
from api.user import user_bp
from api.bookshelf import shelf_bp
from api.recommendations import recommendation_bp

app = Flask(__name__)

# Enable CORS for specific origins and handle OPTIONS requests
CORS(
    app,
    resources={
        r"/*": {"origins": "http://localhost:3000", "supports_credentials": True}
    },
)

# Register API Blueprints
app.register_blueprint(books_bp, url_prefix="/api")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(shelf_bp, url_prefix="/shelf")
app.register_blueprint(recommendation_bp, url_prefix="/recs")


# Explicit handling for preflight OPTIONS requests
@app.before_request
def before_request():
    if request.method == "OPTIONS":
        return "", 200  # Respond with HTTP 200 for OPTIONS requests


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
