from rest_framework import permissions


class IsHostOrJoinableOnly(permissions.BasePermission):
    """
    Custom permission to only allow host of a room to delete or update it
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.host == request.session.session_key
        )


class IsHost(permissions.BasePermission):
    """
    Allow to perform only if user is the host
    """

    message = "You have to be host of the room"

    def has_object_permission(self, request, view, obj):
        return obj.host == request.session.session_key


class InRoom(permissions.BasePermission):
    """
    Allow to perform only if user is in a room
    """

    message = "You have to be in a room"

    def has_permission(self, request, view):
        return "code" in request.session.keys()


class CanPlayPause(permissions.BasePermission):
    """
    Allow to perform only if room
    has specified that users can pause
    """

    message = "You cannot play and pause the song"

    def has_object_permission(self, request, view, room):
        return room.user_can_pause


class CanControl(permissions.BasePermission):
    message = "You cannot control flow of the song"

    def has_object_permission(self, request, view, room):
        return room.user_can_control


class HasNotVoted(permissions.BasePermission):
    message = "You have already voted to skip"

    def has_object_permission(self, request, view, room):

        return request.session.get("last_voted_song") != room.current_song_id


class TrackInPlayer(permissions.BasePermission):
    message = "Nothing is currently playing"

    def has_object_permission(self, request, view, room):

        return room.current_song_id != ""
