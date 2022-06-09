from .credentials import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    SPOTIFY_GET_TOKEN_URL,
)
from base64 import urlsafe_b64encode
import requests


def create_or_refresh_token(room, request_code=None):
    # authorization_value = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        # "Authorization": urlsafe_b64encode(authorization_value.encode("ascii")),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = (
        {
            # "response_type": "code",
            "grant_type": "refresh_token",
            "refresh_token": room.spotify_access_token.refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        if hasattr(room, "spotify_access_token")
        else {
            "response_type": "code",
            "grant_type": "authorization_code",
            "code": request_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    )

    return requests.post(SPOTIFY_GET_TOKEN_URL, headers=headers, data=data)
