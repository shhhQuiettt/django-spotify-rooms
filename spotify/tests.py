import json
import os
from datetime import timedelta
from unittest.mock import patch

from api import permissions as room_permissions
from api.models import Room
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from spotify import permissions as spotify_permissions
from spotify.models import SpotifyAccessToken

from .credentials import SPOTIFY_AUTH_URL, SPOTIFY_GET_TOKEN_URL


#####TEST HELPERS
def create_test_room(
    host="0" * 40,
    votes_to_skip=3,
    user_can_control=False,
    user_can_pause=False,
    current_song_id="",
):

    return Room.objects.create(
        host=host,
        votes_to_skip=votes_to_skip,
        user_can_control=user_can_control,
        user_can_pause=user_can_pause,
        current_song_id=current_song_id,
    )


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
        self.headers = {"Content-Type": "application/json"}

    def json(self):
        return self.json_data


#######


class SpotifyAccessTokenTestCase(TestCase):
    def test_is_expired_is_true_when_expired(self):
        old_time = timezone.now() - timedelta(days=210)
        token = create_test_token()
        token.created_at = old_time
        self.assertTrue(token.is_expired())

    def test_is_expired_is_false_when_not_expired(self):
        token = create_test_token()
        self.assertFalse(token.is_expired())


class SpotifyAuthorizationTestCase(APITestCase):
    def test_authenticate_spotify_redirects(self):
        session = self.client.session
        room = create_test_room(session.session_key)
        session["code"] = room.code
        session.save()

        res = self.client.get(reverse("spotify authorization"))
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
        res = self.client.get(reverse("spotify authorization"))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticate_spotify_when_not_in_room(self):
        res = self.client.get(reverse("spotify authorization"))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_callback_when_token_given(self):
        session = self.client.session
        room = create_test_room(host=session.session_key)
        session["code"] = room.code
        session.save()

        pwd = os.path.dirname(__file__)
        with patch(
            "spotify.views.create_or_refresh_token"
        ) as mocked_create_or_refresh_token:

            with open(
                os.path.join(pwd, "mocks/mock_access_token.json")
            ) as mock_token_file:
                test_token_response = json.load(mock_token_file)

            mocked_create_or_refresh_token.return_value = MockResponse(
                json_data=test_token_response,
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
            with open(os.path.join(pwd, "mocks/mock_song.json")) as mock_song_file:
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

            room.refresh_from_db()

            self.assertEqual(res.data, expected_data)
            self.assertEqual(room.current_song_id, expected_data["song_id"])
            self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_current_track_when_song_changed(self):
        pwd = os.path.dirname(__file__)
        url = reverse("current track")

        room = create_test_room()

        session = self.client.session
        session["code"] = room.code
        session.save()

        create_test_token(room)

        with patch("spotify.utils.requests.get") as mocked_requests_get:
            with open(os.path.join(pwd, "mocks/mock_song.json")) as mock_song_file:
                mocked_requests_get.return_value = MockResponse(
                    json_data=json.load(mock_song_file),
                    status_code=status.HTTP_200_OK,
                )

            res = self.client.get(url)

            old_song_id = res.json()["song_id"]

            with open(os.path.join(pwd, "mocks/mock_song_2.json")) as mock_song_file:
                mocked_requests_get.return_value = MockResponse(
                    json_data=json.load(mock_song_file),
                    status_code=status.HTTP_200_OK,
                )
            res = self.client.get(url)
            new_song_id = res.json()["song_id"]

            room.refresh_from_db()
            self.assertNotEqual(new_song_id, "")
            self.assertNotEqual(old_song_id, new_song_id)


# self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
# self.assertEqual(str(res.data["detail"]), "You have to be host of the room")


class PlayPauseTestCase(APITestCase):
    # TODO: Create shortcuts to provide test context like in romm, logged
    # decorators maybe?

    # PAUSE
    def test_pause_track_when_not_in_a_room_forbidden(self):
        url = reverse("pause track")
        res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(str(res.data["detail"]), room_permissions.InRoom.message)

    def test_pause_track_when_room_rules_not_authorized(self):
        url = reverse("pause track")

        room = create_test_room(user_can_pause=True)

        session = self.client.session
        session["code"] = room.code
        session.save()

        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(res.data["detail"]), spotify_permissions.SpotifyAuthorized.message
        )

    def test_pause_track_when_room_rules_not_allow_forbidden(self):
        url = reverse("pause track")

        room = create_test_room(user_can_pause=False)
        token = create_test_token(room)

        session = self.client.session
        session["code"] = room.code
        session.save()
        with patch("spotify.utils.requests.put") as mocked_requests_put:
            mocked_requests_put.return_value = MockResponse(
                {}, status.HTTP_418_IM_A_TEAPOT
            )
            res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, msg=res.data)

    def test_pause_track_when_allowed(self):
        url = reverse("pause track")

        room = create_test_room(user_can_pause=True)
        token = create_test_token(room)

        session = self.client.session
        session["code"] = room.code
        session.save()

        with patch("spotify.utils.requests.put") as mocked_requests_put:
            mocked_requests_put.return_value = MockResponse(
                {}, status_code=status.HTTP_204_NO_CONTENT
            )
            res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(res.data, None)

    def test_pause_track_when_spotify_error(self):
        url = reverse("pause track")

        room = create_test_room(user_can_pause=True)
        token = create_test_token(room)

        session = self.client.session
        session["code"] = room.code
        session.save()

        with patch("spotify.utils.requests.put") as mocked_requests_put:
            mocked_requests_put.return_value = MockResponse(
                {"error": {"status": 418, "message": "Nie"}},
                status_code=status.HTTP_418_IM_A_TEAPOT,
            )
            res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_418_IM_A_TEAPOT, msg=res.json())
        self.assertEqual(
            res.data, {"spotify": {"error": {"status": 418, "message": "Nie"}}}
        )

    # PLAY
    def test_play_track_when_not_in_a_room_forbidden(self):
        url = reverse("play track")
        res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(str(res.data["detail"]), room_permissions.InRoom.message)

    def test_play_track_when_room_rules_not_authorized(self):
        url = reverse("play track")

        room = create_test_room(user_can_pause=True)

        session = self.client.session
        session["code"] = room.code
        session.save()

        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(res.data["detail"]), spotify_permissions.SpotifyAuthorized.message
        )

    def test_play_track_when_room_rules_not_allow_forbidden(self):
        url = reverse("play track")

        room = create_test_room(user_can_pause=False)
        token = create_test_token(room)

        session = self.client.session
        session["code"] = room.code
        session.save()
        with patch("spotify.utils.requests.put") as mocked_requests_put:
            mocked_requests_put.return_value = MockResponse(
                {}, status.HTTP_403_FORBIDDEN
            )
            res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, msg=res.data)

    def test_play_track_when_allowed(self):
        url = reverse("play track")

        room = create_test_room(user_can_pause=True, user_can_control=False)
        token = create_test_token(room)

        session = self.client.session
        session["code"] = room.code
        session.save()

        with patch("spotify.utils.requests.put") as mocked_requests_put:
            mocked_requests_put.return_value = MockResponse(
                {}, status_code=status.HTTP_204_NO_CONTENT
            )
            res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(res.data, None)

    def test_play_track_when_spotify_error(self):
        url = reverse("play track")

        room = create_test_room(user_can_pause=True)
        token = create_test_token(room)

        session = self.client.session
        session["code"] = room.code
        session.save()

        with patch("spotify.utils.requests.put") as mocked_requests_put:
            mocked_requests_put.return_value = MockResponse(
                {"error": {"status": 418, "message": "Nie"}},
                status_code=status.HTTP_418_IM_A_TEAPOT,
            )
            res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_418_IM_A_TEAPOT, msg=res.json())
        self.assertEqual(
            res.data, {"spotify": {"error": {"status": 418, "message": "Nie"}}}
        )


class VoteToSkipTrackTestCase(APITestCase):
    def test_vote_to_skip_track_when_not_in_a_room(self):
        url = reverse("vote to skip track")
        res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(str(res.data["detail"]), room_permissions.InRoom.message)

    def test_vote_to_skip_track_when_not_authorized(self):
        url = reverse("vote to skip track")

        room = create_test_room(user_can_pause=True)

        session = self.client.session
        session["code"] = room.code
        session.save()

        res = self.client.put(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(res.data["detail"]), spotify_permissions.SpotifyAuthorized.message
        )

    def test_vote_to_skip_track_when_nothing_plays_forbidden(self):
        url = reverse("vote to skip track")

        session = self.client.session

        room = create_test_room(host=session.session_key, votes_to_skip=1)
        create_test_token(room)

        session["code"] = room.code
        session.save()

        with patch("spotify.views.call_spotify_api") as mocked_call_spotify_api:
            mocked_call_spotify_api.return_value = MockResponse(
                {"shouldnt": "be called"}, status.HTTP_418_IM_A_TEAPOT
            )
            res = self.client.put(url)

            self.assertEqual(
                res.json().get("detail"), room_permissions.TrackInPlayer.message
            )
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_vote_to_skip_track_host_always_can_skip(self):
        url = reverse("vote to skip track")

        session = self.client.session

        room = create_test_room(
            host=session.session_key, votes_to_skip=1, current_song_id="123"
        )
        create_test_token(room)

        session["code"] = room.code
        session.save()

        with patch("spotify.views.call_spotify_api") as mocked_call_spotify_api:
            mocked_call_spotify_api.return_value = MockResponse(
                {}, status.HTTP_204_NO_CONTENT
            )
            res = self.client.put(url)

            try:
                mocked_call_spotify_api.assert_called_once()
                self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
            except AssertionError as e:
                print(res.data)
                raise e

    def test_vote_to_skip_when_not_enaugh_votes(self):
        url = reverse("vote to skip track")

        session = self.client.session

        room = create_test_room(votes_to_skip=99, current_song_id="123")
        create_test_token(room)

        session["code"] = room.code
        session.save()

        with patch("spotify.views.call_spotify_api") as mocked_call_spotify_api:
            mocked_call_spotify_api.return_value = MockResponse(
                {}, status.HTTP_418_IM_A_TEAPOT
            )
            res = self.client.put(url)
            room.refresh_from_db()

            try:
                mocked_call_spotify_api.assert_not_called()
                self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
                self.assertEqual(room.current_votes, 1)
            except AssertionError as e:
                print(res.data)
                raise e

    def test_vote_to_skip_when_song_changes_votes_equal_0(self):
        url = reverse("vote to skip track")

        session = self.client.session

        room = create_test_room(votes_to_skip=99, current_song_id="123")
        create_test_token(room)

        session["code"] = room.code
        session.save()

        with patch("spotify.views.call_spotify_api") as mocked_call_spotify_api:
            mocked_call_spotify_api.return_value = MockResponse(
                {}, status.HTTP_418_IM_A_TEAPOT
            )

            self.assertEqual(room.current_votes, 0)

            res = self.client.put(url)
            room.refresh_from_db()
            self.assertEqual(room.current_votes, 1)

            pwd = os.path.dirname(__file__)
            with open(os.path.join(pwd, "mocks/mock_song.json")) as song_mock_file:
                mocked_call_spotify_api.return_value = MockResponse(
                    json.load(song_mock_file), status.HTTP_200_OK
                )

            self.client.get(reverse("current track"))
            room.refresh_from_db()
            self.assertEqual(room.current_votes, 0)

    def test_vote_to_skip_track_when_enaugh_votes(self):
        url = reverse("vote to skip track")
        second_client = APIClient()

        second_client_session = second_client.session
        session = self.client.session

        room = create_test_room(votes_to_skip=2, current_song_id="123")
        create_test_token(room)

        session["code"] = room.code
        session.save()
        second_client_session["code"] = room.code
        second_client_session.save()

        with patch("spotify.views.call_spotify_api") as mocked_call_spotify_api:
            mocked_call_spotify_api.return_value = MockResponse(
                {}, status.HTTP_204_NO_CONTENT
            )
            self.client.put(url)
            mocked_call_spotify_api.assert_not_called()

            second_client.put(url)
            mocked_call_spotify_api.assert_called()

            room.refresh_from_db()
            self.assertEqual(room.current_votes, 0)
