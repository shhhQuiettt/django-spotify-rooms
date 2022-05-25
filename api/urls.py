from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create-room/", views.create_room, name="create room"),
    path("join-room/", views.join_room, name="join room"),
]
