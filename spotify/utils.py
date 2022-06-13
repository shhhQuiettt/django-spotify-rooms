from .credentials import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    SPOTIFY_GET_TOKEN_URL,
    SPOTIFY_API_BASE_URL,
)
from base64 import urlsafe_b64encode
import requests

# TODO: this function should create token instance or be renamed to  get_...
def create_or_refresh_token(room, request_code=None):
    # authorization_value = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        # "Authorization": urlsafe_b64encode(authorization_value.encode("ascii")),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = (
        {
            "response_type": "code",
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


def call_spotify_api(endpoint, token, method="GET", data={}):
    """
    Executes a spotify api request
    """
    headers = {
        "Authorization": f"Bearer {token}",
    }

    if method not in ["GET", "POST", "PUT"]:
        raise ValueError("Method has to be GET, POST or PUT")

    if method == "GET":
        res = requests.get(SPOTIFY_API_BASE_URL + endpoint, data, headers=headers)
    elif method == "POST":
        res = requests.post(SPOTIFY_API_BASE_URL + endpoint, data, headers=headers)
    else:
        res = requests.put(SPOTIFY_API_BASE_URL + endpoint, data, headers=headers)

    return res
