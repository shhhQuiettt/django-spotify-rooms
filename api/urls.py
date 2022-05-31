from django.urls import path

from . import views

urlpatterns = [
    path("room/create", views.RoomView.as_view(), name="create room"),
    # path("room/<str:code>", views.join_room, name="room detail"),
]
