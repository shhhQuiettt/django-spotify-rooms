from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import RoomSerializer
from .models import Room
import logging

# Create your views here.


class RoomView(generics.GenericAPIView, mixins.CreateModelMixin):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def perform_create(self, serializer):
        serializer.save(host=self.request.session.session_key)

    def post(self, request, *args, **kwargs):
        if Room.objects.filter(host=request.session.session_key).exists():
            return Response(
                data={
                    "error": "You already have a room created",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.session.exists(request.session.session_key):
            request.session.create()

        return self.create(request, *args, **kwargs)


# def room_api(request):
#     # JEŻELI SESJA ISTNIEJE PRZYPISZ KOD I is_host, W PRZECIWNYM ZWRÓĆ 404
#     if True:
#         code = "000000"
#         host = True
#     room = get_object_or_404(Room, code)

#     if request.method == "GET":
#         pass
#     if request.method == "DELETE":
#         if host:
#             room.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
