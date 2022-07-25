from rest_framework.test import APITestCase, APIClient
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.urls import reverse
from .models import Room
from .shortcuts import room_code_or_403, is_host_or_403


def create_room(host="0" * 40, votes_to_skip=3):
    data = {
        "host": host,
        "votes_to_skip": votes_to_skip,
    }
    return Room.objects.create(**data)


class RoomTestCase(APITestCase):
    retrieve_fields = set(
        [
            "code",
            "votes_to_skip",
            "user_can_control",
            "user_can_pause",
            "created_at",
            "current_song_id",
        ]
    )

    def test_create_room_new_room(self):
        url = reverse("create room")
        data = {
            "votes_to_skip": 3,
        }
        response = self.client.post(url, data, format="json")
        session = self.client.session

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Room.objects.count(), 1)
        room = Room.objects.get()
        self.assertEqual(room.host, session.session_key)
        self.assertIn("code", session.keys())

    def test_create_room_when_already_created(self):
        url = reverse("create room")
        data = {
            "votes_to_skip": 3,
        }
        self.client.post(url, data, format="json")
        session = self.client.session
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Room.objects.count(), 1)

    def test_get_room_with_notexisting_code(self):
        room = create_room()
        url = reverse("room detail", args=["111111"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_room_with_proper_code(self):
        room = create_room()
        proper_code = room.code
        url = reverse("room detail", args=[proper_code])
        response = self.client.get(url)
        session = self.client.session

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.retrieve_fields)

    def test_delete_room_when_not_the_host(self):
        session = self.client.session
        room = create_room(session.session_key)

        bad_actor = APIClient()

        url = reverse("room detail", args=[room.code])
        response = bad_actor.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Room.objects.filter(code=room.code).exists())

    def test_delete_room_when_host(self):
        session = self.client.session
        room = create_room(session.session_key)

        url = reverse("room detail", args=[room.code])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Room.objects.filter(code=room.code).exists())

    def test_update_room_when_host(self):
        session = self.client.session
        room = create_room(host=session.session_key, votes_to_skip=3)

        new_data = {"votes_to_skip": 11}

        url = reverse("room detail", args=[room.code])
        response = self.client.put(url, data=new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Room.objects.get(code=room.code).votes_to_skip, new_data["votes_to_skip"]
        )

    def test_update_room_when_not_the_host(self):
        session = self.client.session
        room = create_room(host=session.session_key, votes_to_skip=3)
        old_votes_to_skip = room.votes_to_skip

        bad_actor = APIClient()
        new_data = {"votes_to_skip": 11}

        url = reverse("room detail", args=[room.code])
        response = bad_actor.put(url, data=new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Room.objects.get(code=room.code).votes_to_skip, old_votes_to_skip
        )


class ShortcutsTestCase(APITestCase):
    def test_room_code_or_403_when_exists(self):
        room = create_room()
        session = self.client.session
        session["code"] = room.code
        code = room_code_or_403(session)
        self.assertEqual(code, room.code)

    def test_room_code_or_403_when_not_in_room(self):
        room = create_room()
        session = self.client.session
        self.assertRaises(PermissionDenied, room_code_or_403, session)

    def test_is_host_or_403_when_host(self):
        session = self.client.session
        room = create_room(host=session.session_key)

        is_host_or_403(room, session)

    def test_is_host_or_403_when_not_host(self):
        session = self.client.session

        room = create_room()

        self.assertRaises(
            PermissionDenied,
            is_host_or_403,
            room,
            session,
        )
