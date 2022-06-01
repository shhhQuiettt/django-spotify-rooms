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
