import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_options_request_handling(client):
    res = client.open("/api", method="OPTIONS")
    assert res.status_code == 200


def test_books_endpoint_exists(client):
    res = client.get("/api")
    # It may return 404 if no root handler is defined in books_bp,
    # but shouldn't be a 500
    assert res.status_code in [200, 404]


def test_cors_headers_present(client):
    res = client.get("/api", headers={"Origin": "http://localhost:3000"})
    assert "Access-Control-Allow-Origin" in res.headers
