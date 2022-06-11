from django.db import models
from api.models import Room


class SpotifyAccessToken(models.Model):
    room = models.OneToOneField(
        Room,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="spotify_access_token",
    )
    token = models.CharField(max_length=2048)
    token_type = models.CharField(max_length=32)
    scope = models.CharField(max_length=200)
    refresh_token = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now=True)
    expires_in = models.PositiveIntegerField()
