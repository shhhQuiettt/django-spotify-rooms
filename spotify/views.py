from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .credentials import (
    SPOTIFY_AUTH_URL,
    SPOTIFY_GET_TOKEN_URL,
    CLIENT_ID,
    SCOPE,
    REDIRECT_URI,
    STATE,
    CLIENT_SECRET,
)
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
import requests
from base64 import b64encode

# Create your views here.


@api_view(["GET"])
def authenticate_spotify(request):
    print(REDIRECT_URI)
    if request.method == "GET":
        redirect_data = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "scope": SCOPE,
            "redirect_uri": REDIRECT_URI,
            "state": STATE,
        }
        url = f"{SPOTIFY_AUTH_URL}?{urlencode(redirect_data)}"
        return redirect(url, permanent=True)


@api_view(["GET"])
def authentication_callback(request):
    if request.method == "GET":
        if request.query_params.get("error"):
            return Response(
                {
                    "error": request.data.get("error"),
                    "message": "Spotify authorization error",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        code = request.query_params["code"]
        state = request.query_params["state"]

        get_token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }

        authorization_value = f"{CLIENT_ID}:{CLIENT_SECRET}"
        get_token_headers = {
            "Authorization": b"Basic " + b64encode(authorization_value.encode("ascii")),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        res = requests.post(
            url=SPOTIFY_GET_TOKEN_URL, headers=get_token_headers, data=get_token_data
        )

        return Response(res.json())
