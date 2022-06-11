import os
from dotenv import load_dotenv
from django.utils.crypto import get_random_string
from django.urls import reverse_lazy

load_dotenv()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
# REDIRECT_URI = reverse_lazy("authorization callback")
REDIRECT_URI = "http://localhost:8000/spotify/auth-callback"
STATE = get_random_string(16)
SCOPE = (
    "user-read-playback-state user-modify-playback-state user-read-currently-playing"
)
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_GET_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
