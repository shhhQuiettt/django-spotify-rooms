from django.urls import path

from . import views

urlpatterns = [
    path("auth", views.authenticate_spotify, name="spotify authorization"),
    path("auth-callback", views.authentication_callback, name="authorization callback"),
    path("refresh-token", views.refresh_token),
    path("track/current", views.CurrentTrack.as_view(), name="current track"),
    path("track/pause", views.PauseTrack.as_view(), name="pause track"),
    path("track/play", views.PlayTrack.as_view(), name="play track"),
    path(
        "track/vote-to-skip", views.VoteToSkipTrack.as_view(), name="vote to skip track"
    ),
]
