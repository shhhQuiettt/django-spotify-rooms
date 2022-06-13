from rest_framework.exceptions import PermissionDenied


def room_code_or_403(session):
    code = session.get("code")
    if code is None:
        raise PermissionDenied(detail="You have to be in a room first")

    return code


def is_host_or_403(room, session):
    if not room.is_host(session):
        raise PermissionDenied(detail="Yout have to be a host of the room")
