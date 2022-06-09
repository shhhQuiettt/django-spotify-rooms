from .serializers import SpotifyAccessTokenSerializer
from .utils import create_or_refresh_token
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.shortcuts import room_code_or_403, is_host_or_403
from api.models import Room
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
from time import time


@api_view(["GET"])
# TODO: implement permission approach
# @permission_classes([IsHost])
def authenticate_spotify(request):
    if request.method == "GET":
        # Checks if user is in a room and if he is the host
        room_code = room_code_or_403(request.session)

        is_host_or_403(get_object_or_404(Room, code=room_code), request.session)

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

        room_code = room_code_or_403(request.session)
        room = get_object_or_404(Room, code=room_code)
        is_host_or_403(room, request.session)

        # Obtaining access token
        request_code = request.query_params["code"]
        state = request.query_params["state"]

        res = create_or_refresh_token(room, request_code)

        if res.status_code != status.HTTP_200_OK:
            return Response({"errors": res.json()}, status=status.HTTP_401_UNAUTHORIZED)

        data = res.json()
        data["room"] = room.code
        serializer = SpotifyAccessTokenSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {"message": "Successfully authorized"}, status=status.HTTP_200_OK
        )


@api_view(["POST"])
# TODO: implement permission approach
# @permission_classes([IsHost])
def refresh_token(request):
    if request.method == "POST":
        # Checks if user is in a room and if he is the host
        room_code = room_code_or_403(request.session)
        room = get_object_or_404(Room, code=room_code)
        is_host_or_403(room, request.session)

        if not hasattr(room, "spotify_access_token"):
            return Response(
                {"error": "Nothing to refresh", "message": "Token does not exists"},
                status=status.HTTP_403_FORBIDDEN,
            )

        res = create_or_refresh_token(room)
        data = res.json()
        data["room"] = room.code

        if res.status_code != status.HTTP_200_OK:
            return Response({"errors": res.json()}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SpotifyAccessTokenSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

        return Response(
            {"message": "Successfully refreshed"}, status=status.HTTP_200_OK
        )
