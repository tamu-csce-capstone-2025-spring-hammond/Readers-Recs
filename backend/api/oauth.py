# import os
import requests
from fastapi import APIRouter, HTTPException
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse

config = Config(".env")  # Load from environment variables or .env file

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="your-client-id")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", default="your-client-secret")
GOOGLE_REDIRECT_URI = config(
    "GOOGLE_REDIRECT_URI", default="http://localhost:8000/auth/callback"
)

router = APIRouter()


# Step 1: Redirect user to Google OAuth
@router.get("/auth/google")
async def google_login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(google_auth_url)


# Step 2: Handle OAuth Callback
@router.get("/auth/callback")
async def google_callback(request: Request, code: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        raise HTTPException(status_code=400, detail="Failed to fetch the token")

    access_token = token_json["access_token"]

    # Step 3: Get User Info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    return {"user": user_info, "access_token": access_token}
