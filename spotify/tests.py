import os
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework import status
from .credentials import SPOTIFY_AUTH_URL, SPOTIFY_GET_TOKEN_URL
from django.urls import reverse
from api.models import Room
from spotify.models import SpotifyAccessToken
from unittest.mock import patch
import json


def create_test_room(host="0" * 40, votes_to_skip=3):
    data = {
        "host": host,
        "votes_to_skip": votes_to_skip,
    }
    return Room.objects.create(**data)


def create_test_token(room=None):
    room = create_test_room() if room is None else room
    test_token = {
        "token": "BAghSW8TbttNHo4PqsdfgsdgggghhhhhN2110rn8tAdVSteKPN_KCGYmobKdUxJrh0bWlCYa7WuZJer9E8lqJA608w65Sar8ayeJ1m6rmwzQ5wCn38Wji9DR3LiBv-RYDADeYcdMssEGBIkndwftAjv8hxEWLbdlWGekK5QZdcceozVCAkMIQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "A3BS0meP8fmcJegBsrGpyp8kzygfgfgfhhlmGdkIla_8Th2ZMsgXd8Xd7n7lagDhTgzDBHkeSke4SgE7H9895EtyTj6UWdwlemHw02sIj-Sn88vlXtBWfOM0_YfFiYKOjV2w_OY",
        "scope": "user-modify-playback-state user-read-playback-state user-read-currently-playing",
        "room": room,
    }
    return SpotifyAccessToken.objects.create(**test_token)


class MockResponse:
    """
    Used to mock create_or_refresh_token api call
    """

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class SpotifyAuthorizationTestCase(APITestCase):
    def test_authenticate_spotify_redirects(self):
        session = self.client.session
        room = create_test_room(session.session_key)
        session["code"] = room.code
        session.save()

        res = self.client.get(reverse("spotify_authorization"))
        self.assertEqual(
            res.status_code,
            status.HTTP_301_MOVED_PERMANENTLY,
            msg=f"Response data: {res.get('data')}",
        )
        # assertRedirects doesnt have common unittest "msg" parameter
        # try:
        #     self.assertRedirects(
        #         res,
        #         SPOTIFY_AUTH_URL,
        #         status_code=status.HTTP_301_MOVED_PERMANENTLY,
        #         fetch_redirect_response=False,
        #     )
        # except AssertionError as e:
        #     if hasattr(res, "data"):
        #         print(res.data)
        #     raise e

    def test_authenticate_spotify_when_not_host(self):
        session = self.client.session
        room = create_test_room()
        session["code"] = room.code
        session.save()
        res = self.client.get(reverse("spotify_authorization"))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticate_spotify_when_not_in_room(self):
        res = self.client.get(reverse("spotify_authorization"))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_callback_when_token_given(self):
        session = self.client.session
        room = create_test_room(host=session.session_key)
        session["code"] = room.code
        session.save()

        with patch(
            "spotify.views.create_or_refresh_token"
        ) as mocked_create_or_refresh_token:
            mocked_create_or_refresh_token.return_value = MockResponse(
                json_data=create_test_token(),
                status_code=status.HTTP_200_OK,
            )

            res = self.client.get(
                reverse("authorization callback"),
                {"code": "1234", "state": "123"},
            )

            self.assertEqual(res.status_code, status.HTTP_200_OK, msg=f"{res.data}")
            self.assertEqual(
                SpotifyAccessToken.objects.filter(room=room.code).count(), 1
            )
            self.assertTrue(hasattr(room, "spotify_access_token"))

    def test_authentication_callback_when_error_given(self):
        session = self.client.session
        room = create_test_room(host=session.session_key)
        session["code"] = room.code
        session.save()

        with patch(
            "spotify.views.create_or_refresh_token"
        ) as mocked_create_or_refresh_token:
            mocked_create_or_refresh_token.return_value = MockResponse(
                json_data={
                    "error": "Some error",
                    "error_message": "Something went wrong",
                },
                status_code=status.HTTP_418_IM_A_TEAPOT,
            )

            res = self.client.get(
                reverse("authorization callback"),
                {"code": "1234", "state": "123"},
            )

            self.assertEqual(
                res.status_code, status.HTTP_401_UNAUTHORIZED, msg=f"{res.data}"
            )
            self.assertEqual(
                SpotifyAccessToken.objects.filter(room=room.code).count(), 0
            )
            self.assertFalse(hasattr(room, "spotify_access_token"))


class TrackControlTestCase(APITestCase):
    def test_current_track_when_not_in_a_room_is_forbidden(self):
        url = reverse("current track")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(res.data["detail"]), "You have to be in a room", msg=f"{res.data}"
        )

    def test_current_track_when_not_authorized_forbidden(self):
        room = create_test_room()
        session = self.client.session
        session["code"] = room.code
        session.save()

        url = reverse("current track")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(res.data["detail"]),
            "You have to log into spotify first",
            msg=f"{res.data}",
        )

    def test_current_track_when_not_a_host_permited(self):
        pwd = os.path.dirname(__file__)
        url = reverse("current track")

        room = create_test_room()

        session = self.client.session
        session["code"] = room.code
        session.save()

        create_test_token(room)

        with patch("spotify.utils.requests.get") as mocked_requests_get:
            with open(os.path.join(pwd, "test_data/mock_song.json")) as mock_song_file:
                mocked_requests_get.return_value = MockResponse(
                    json_data=json.load(mock_song_file),
                    status_code=status.HTTP_200_OK,
                )

            res = self.client.get(url)

            expected_data = {
                "title": "Bardziej Sobą Niż Kiedykolwiek",
                "duration_s": 211.956,
                "progress_s": 61.010,
                "album_cover_url": "https://i.scdn.co/image/ab67616d0000b273eedbeb9aa41628df56530f44",
                "is_playing": True,
                "song_id": "00KWg3ywQZVELTUa1U2vsx",
                "artists": "Oki",
            }

            self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
            self.assertEqual(res.data, expected_data)

        # self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(str(res.data["detail"]), "You have to be host of the room")
