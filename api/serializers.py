from rest_framework import serializers
from .models import Room


class RoomRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "code",
            "votes_to_skip",
            "user_can_pause",
            "user_can_control",
            "created_at",
            "current_song_id",
        ]

    code = serializers.ReadOnlyField()
    current_song_id = serializers.ReadOnlyField()


# TODO: Creating room shouldn't return host key
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "code",
            "host",
            "votes_to_skip",
            "user_can_pause",
            "user_can_control",
            "created_at",
            "current_song_id",
        ]

    code = serializers.ReadOnlyField()
    host = serializers.ReadOnlyField()
