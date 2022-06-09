from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCaseuth-callback?code=AQBDADr9GnVcRsIms3YXtOKMPGp8h4T8Da8bAu-gKH2kdTQ_XTbMyFdQp_yZnkg4gZWawrxjjo9O1Zuq1WXWHkrblQQqHhQCYaM5lNT-ayAYgdOR7DDpsNbb4-UcOQFqJZnorIB9qurbCJPuyPsAHJEeGGwX9qF57I7y_VE8VtPY-H0vJGFiIpCu97vABq56zEztFN9kduP0CQ9dXH0gsywGP72k1Sa63dD4AEDBLayalP0M7gixP6pKnmzSnmOJB-1lwRDFjAq_IRK_R1zG3MsaIaW9XvmkL5DJKRc1UsQl1A&state=gl9ddUjau1VcAWVn
from .credentials import SPOTIFY_AUTH_URL, SPOTIFY_GET_TOKEN_URL
from django.urls import reverse
from api.models import Room


def create_room(host="0" * 40, votes_to_skip=3):
    data = {
        "host": host,
        "votes_to_skip": votes_to_skip,
    }
    return Room.objects.create(**data)


def get_test_spotify_token():
    test_token = {}


class SpotifyTestCase(APITestCase):
    def test_authenticate_spotify_redirects(self):
        session = self.client.session
        room = create_room(session.session_key)
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
        room = create_room()
        session["code"] = room.code
        session.save()
        res = self.client.get(reverse("spotify_authorization"))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticate_spotify_when_not_in_room(self):
        res = self.client.get(reverse("spotify_authorization"))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_callback_when_token_given(self):
        session = self.client.session
        room = create_room(session.session_key)
        session["code"] = room.code
        session.save()

        res = self.client.get(reverse("spotify_authorization"))

    def test_authentication_callback_when_error_given(self):
        session = self.client.session
        room = create_room(session.session_key)
        session["code"] = room.code
        session.save()

        res = self.client.get(reverse("spotify_authorization"))

