# tests/unit_tests/api_tests/oauth_api_test.py
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.oauth import router  # make sure this matches the path to your router file

app = FastAPI()
app.include_router(router)  # This must be included for the routes to be found
client = TestClient(app)


def test_google_login_redirect():
    response = client.get("/auth/google")
    # assert response.status_code in [307, 200]
    # assert "https://accounts.google.com/o/oauth2/auth" in response.headers.get("location", "")


@patch("api.oauth.requests.get")
@patch("api.oauth.requests.post")
def test_google_callback_success(mock_post, mock_get):
    # Mock token exchange
    mock_post.return_value.json.return_value = {"access_token": "mock_access_token"}

    # Mock user info retrieval
    mock_get.return_value.json.return_value = {
        "email": "test@example.com",
        "name": "Test User",
        "id": "123456",
    }

    response = client.get("/auth/callback?code=testcode")
    assert response.status_code == 200
    assert "user" in response.json()
    assert response.json()["user"]["email"] == "test@example.com"


@patch("api.oauth.requests.post")
def test_google_callback_token_failure(mock_post):
    mock_post.return_value.json.return_value = {}  # No access_token in response

    response = client.get("/auth/callback?code=badcode")
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to fetch the token"


def test_google_callback_no_code():
    response = client.get("/auth/callback")
    assert response.status_code == 400
    assert response.json()["detail"] == "Authorization code not provided"
