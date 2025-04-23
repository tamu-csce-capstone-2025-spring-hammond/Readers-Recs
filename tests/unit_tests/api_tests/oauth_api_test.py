# import pytest
# from starlette.testclient import TestClient
# from oauth import router
# from fastapi import FastAPI

# app = FastAPI()
# app.include_router(router)

# client = TestClient(app)

# def test_google_login_redirect():
#     response = client.get("/auth/google", allow_redirects=False)
#     assert response.status_code == 307 or response.status_code == 302
#     assert "accounts.google.com" in response.headers["location"]

# def test_google_callback_no_code():
#     response = client.get("/auth/callback")
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Authorization code not provided"
