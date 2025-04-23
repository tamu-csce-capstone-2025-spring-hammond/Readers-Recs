import pytest
from main import app

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
