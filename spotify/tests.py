from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework import status
from .credentials import SPOTIFY_AUTH_URL, SPOTIFY_GET_TOKEN_URL
from django.urls import reverse
from api.models import Room
from spotify.models import SpotifyAccessToken
from unittest.mock import patch


def create_test_room(host="0" * 40, votes_to_skip=3):
    data = {
        "host": host,
        "votes_to_skip": votes_to_skip,
    }
    return Room.objects.create(**data)


def get_test_token():
    test_token = {
        "access_token": "BAghSW8TbttNHo4Pq1oSHPSpA3N2110rn8tAdVSteKPN_KCGYmobKdUxJrh0bWlCYa7WuZJer9E8lqJA608w65Sar8ayeJ1m6rmwzQ5wCn38Wji9DR3LiBv-RYDADeYcdMssEGBIkndwftAjv8hxEWLbdlWGekK5QZdcceozVCAkMIQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "A3BS0meP8fmcJegBsrGpyp8kzyaseWqmGdkIla_8Th2ZMsgXd8Xd7n7lagDhTgzDBHkeSke4SgE7H9895EtyTj6UWdwlemHw02sIj-Sn88vlXtBWfOM0_YfFiYKOjV2w_OY",
        "scope": "user-modify-playback-state user-read-playback-state user-read-currently-playing",
    }
    return test_token


class MockResponse:
    """
    Used to mock create_or_refresh_token api call
    """

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class SpotifyTestCase(APITestCase):
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
                json_data=get_test_token(),
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
