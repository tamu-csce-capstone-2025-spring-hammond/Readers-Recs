from flask import Flask
from backend.api.books import books_bp

app = Flask(__name__)


# Register the books API Blueprint
app.register_blueprint(books_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
