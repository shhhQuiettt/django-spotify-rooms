from rest_framework import serializers
from datetime import datetime
from .models import SpotifyAccessToken

# from time import


class SpotifyAccessTokenSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(source="token")

    class Meta:
        model = SpotifyAccessToken
        fields = [
            "room",
            "access_token",
            "token_type",
            "scope",
            "refresh_token",
            "expires_in",
        ]
