from time import time

import requests
from api.models import Room
from api.permissions import (
    InRoom,
    IsHost,
    CanPlayPause,
    CanControl,
    HasNotVoted,
    TrackInPlayer,
)
from api.shortcuts import is_host_or_403, room_code_or_403
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse

from spotify.permissions import SpotifyAuthorized

from .credentials import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    SCOPE,
    SPOTIFY_AUTH_URL,
    SPOTIFY_GET_TOKEN_URL,
    STATE,
)
from .serializers import SpotifyAccessTokenSerializer
from .utils import call_spotify_api, create_or_refresh_token


# Sends url for spotify authorization process
@api_view(["GET"])
# TODO: implement permission approach
# @permission_classes([IsHost])
def authenticate_spotify(request):
    if request.method == "GET":
        # Checks if user is in a room and if he is the host
        room_code = room_code_or_403(request.session)

        room = get_object_or_404(Room, code=room_code)
        is_host_or_403(room, request.session)

        redirect_data = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "scope": SCOPE,
            "redirect_uri": REDIRECT_URI,
            "state": STATE,
        }
        url = f"{SPOTIFY_AUTH_URL}?{urlencode(redirect_data)}"

        return Response(
            {"code": room_code, "url": url, "votes_to_skip": room.votes_to_skip}
        )


# TODO: Change to class-based view =>
# => implement create mixin
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

        # TODO: Permissions would be much better solution right?
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

        # return Response(
        #     {"message": "Successfully authorized"}, status=status.HTTP_200_OK
        # )
        return redirect(reverse("front room"))


# TODO: implement class-basef view nad generics update
@api_view(["POST"])
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

        if res.status_code != status.HTTP_200_OK:
            return Response({"errors": res.json()}, status=status.HTTP_401_UNAUTHORIZED)

        data = res.json()
        data["room"] = room.code
        data["refresh_token"] = room.spotify_access_token.refresh_token

        serializer = SpotifyAccessTokenSerializer(room.spotify_access_token, data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return redirect(
            {"message": "Successfully refreshed"}, status=status.HTTP_200_OK
        )


class CurrentTrack(APIView):
    permission_classes = [InRoom, SpotifyAuthorized]

    def get(self, request):
        GET_TRACK_ENDPOINT = "/me/player/currently-playing"

        room_code = request.session["code"]
        room = get_object_or_404(Room, code=room_code)
        self.check_object_permissions(request, room)

        # Refresh token if expired
        # print(f"In roomm ad {room.spotify_access_token.is_expired()}")
        if room.spotify_access_token.is_expired():
            res = create_or_refresh_token(room)
            if res.status_code != status.HTTP_200_OK:
                return Response(
                    {"errors": res.json()}, status=status.HTTP_401_UNAUTHORIZED
                )
            serializer = SpotifyAccessTokenSerializer(
                room.spotify_access_token, res.json(), partial=True
            )
            serializer.is_valid(raise_exception=True)

            serializer.save()

        res = call_spotify_api(
            GET_TRACK_ENDPOINT, token=room.spotify_access_token.token
        )

        if res.status_code >= 300:
            return Response(res.json(), res.status_code)

        if res.status_code == status.HTTP_204_NO_CONTENT:
            return Response(
                {"message": "No current track provided"},
                status=status.HTTP_204_NO_CONTENT,
            )

        data = res.json()
        song_data = {}
        song_data["title"] = data["item"]["name"]
        song_data["duration_s"] = data["item"]["duration_ms"] / 1000
        song_data["progress_s"] = data["progress_ms"] / 1000
        song_data["album_cover_url"] = data["item"]["album"]["images"][0]["url"]
        song_data["is_playing"] = data["is_playing"]
        song_data["song_id"] = data["item"]["id"]

        aritsts = ", ".join([artist["name"] for artist in data["item"]["artists"]])

        song_data["artists"] = aritsts
        song_data["current_votes"] = room.current_votes

        # Save currnet song id to room instance
        if room.current_song_id != song_data["song_id"]:
            room.current_song_id = song_data["song_id"]
            room.current_votes = 0
            room.save()

        return Response(song_data, status=status.HTTP_200_OK)


class PauseTrack(APIView):
    permission_classes = [InRoom, SpotifyAuthorized, CanPlayPause | IsHost]

    def put(self, request):
        room_code = request.session["code"]
        room = get_object_or_404(Room, code=room_code)
        self.check_object_permissions(request, room)

        res = call_spotify_api(
            "/me/player/pause", token=room.spotify_access_token.token, method="PUT"
        )

        if res.status_code >= 400:
            res_data = (
                {"spotify": res.json()}
                if res.headers.get("Content-Type").startswith("application/json")
                else {}
            )
            return Response(res_data, status=res.status_code)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayTrack(APIView):
    permission_classes = [InRoom, SpotifyAuthorized, IsHost | CanPlayPause]

    def put(self, request):
        room_code = request.session["code"]
        room = get_object_or_404(Room, code=room_code)
        self.check_object_permissions(request, room)

        res = call_spotify_api(
            "/me/player/play", token=room.spotify_access_token.token, method="PUT"
        )

        if res.status_code >= 400:
            res_data = (
                {"spotify": res.json()}
                if res.headers.get("Content-Type").startswith("application/json")
                else {}
            )
            return Response(res_data, status=res.status_code)

        return Response(status=res.status_code)


class VoteToSkipTrack(APIView):
    permission_classes = [InRoom, SpotifyAuthorized, TrackInPlayer, HasNotVoted]

    def put(self, request):
        room_code = request.session["code"]
        room = get_object_or_404(Room, code=room_code)
        self.check_object_permissions(request, room)
        # res = call_spotify_api(
        #     "/me/player/next", token=room.spotify_access_token.token, method="POST"
        # )
        # return Response(res.json(), 200)

        room.current_votes += 1
        request.session["last_voted_song"] = room.current_song_id

        if room.is_host(request.session) or room.current_votes >= room.votes_to_skip:
            res = call_spotify_api(
                "/me/player/next", token=room.spotify_access_token.token, method="POST"
            )

            if res.status_code >= 400:
                res_data = (
                    {"spotify": res.json()}
                    if response.headers.get("Content-Type").startswith(
                        "application/json"
                    )
                    else {}
                )
                return Response(res_data, status=res.status_code)

            room.current_votes = 0

        room.save()

        status_code = (
            status.HTTP_204_NO_CONTENT if "res" not in locals() else res.status_code
        )
        return Response(status=status_code)
