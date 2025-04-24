import pytest
from main import app
from api.recommendations import objectid_to_str
from bson import ObjectId
from unittest.mock import patch

app.testing = True


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_onboarding_recommendations_missing_auth(client):
    response = client.post(
        "/recs/api/user/onboarding/recommendations", json={"genres": ["fiction"]}
    )
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_get_recommendations_invalid_user(client):
    response = client.get("/recs/api/user/invalid_id/recommendations")
    assert response.status_code in [400, 500]


def test_objectid_to_str_valid():
    oid = ObjectId()
    result = objectid_to_str(oid)
    assert result == str(oid)
    assert isinstance(result, str)


def test_objectid_to_str_invalid():
    result = objectid_to_str("not_an_objectid")
    assert result is None


@patch(
    "api.recommendations.recommend_books",
    return_value=[{"_id": ObjectId(), "title": "Sample Book"}],
)
def test_get_recommendations_valid_books_returned(mock_recs, client):
    response = client.get("/recs/api/user/abc123/recommendations?refresh_count=2")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["user_id"] == "abc123"
    assert isinstance(json_data["recommendations"], list)
    assert all(
        "_id" in book and isinstance(book["_id"], str)
        for book in json_data["recommendations"]
    )


def test_onboarding_missing_auth_header(client):
    response = client.post("/recs/api/user/onboarding/recommendations")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Missing or invalid Authorization header"


@patch("api.recommendations.requests.get")
def test_onboarding_invalid_token(mock_get, client):
    mock_get.return_value.json.return_value = {"invalid": "no_email"}
    headers = {"Authorization": "Bearer fake_token"}
    response = client.post("/recs/api/user/onboarding/recommendations", headers=headers)
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid token"


@patch("api.recommendations.read_user_by_email", return_value=None)
@patch("api.recommendations.requests.get")
def test_onboarding_user_not_found(mock_token, mock_user, client):
    mock_token.return_value.json.return_value = {"email": "user@example.com"}
    headers = {"Authorization": "Bearer test_token"}
    response = client.post("/recs/api/user/onboarding/recommendations", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"


@patch("api.recommendations.onboarding_recommendations", return_value=True)
@patch("api.recommendations.read_user_by_email")
@patch("api.recommendations.requests.get")
def test_onboarding_recommendations_success(
    mock_token, mock_user, mock_onboard, client
):
    mock_token.return_value.json.return_value = {"email": "user@example.com"}
    mock_user.return_value = {"_id": str(ObjectId())}
    headers = {"Authorization": "Bearer test_token"}
    response = client.post(
        "/recs/api/user/onboarding/recommendations",
        headers=headers,
        json={"genres": ["Fantasy", "Mystery"]},
    )
    assert response.status_code == 200
    assert response.get_json()["genres_updated"] is True


@patch("api.recommendations.requests.get", side_effect=Exception("OAuth failure"))
def test_onboarding_recommendations_internal_error(mock_get, client):
    headers = {"Authorization": "Bearer broken"}
    response = client.post(
        "/recs/api/user/onboarding/recommendations",
        headers=headers,
        json={"genres": ["Fantasy"]},
    )
    assert response.status_code == 500
    assert "error" in response.get_json()
