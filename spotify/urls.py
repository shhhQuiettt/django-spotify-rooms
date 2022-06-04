from django.urls import path

from . import views

urlpatterns = [
    path("auth", views.authenticate_spotify, name="authorize spotify"),
    path("auth-callback", views.authentication_callback, name="authorization callback"),
]
