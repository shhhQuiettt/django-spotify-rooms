from rest_framework.permissions import BasePermission


class SpotifyAuthorized(BasePermission):
    message = "You have to log into spotify first"

    def has_object_permission(self, request, view, room):
        # obj is room
        return hasattr(room, "spotify_access_token") and hasattr(
            room.spotify_access_token, "token"
        )
