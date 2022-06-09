from django.urls import path

from . import views

urlpatterns = [
    path("auth", views.authenticate_spotify, name="spotify_authorization"),
    path("auth-callback", views.authentication_callback, name="authorization callback"),
    path("refresh-token", views.refresh_token),
]
