from django.urls import path

from . import views

urlpatterns = [
    path("room/create", views.RoomCreateView.as_view(), name="create room"),
    path("room/<str:code>", views.RoomView.as_view(), name="room detail"),
]
