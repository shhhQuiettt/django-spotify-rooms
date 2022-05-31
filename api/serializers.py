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
        ]

    code = serializers.ReadOnlyField()


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
        ]

    code = serializers.ReadOnlyField()
    host = serializers.ReadOnlyField()
