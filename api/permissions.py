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
