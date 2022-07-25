from django.shortcuts import get_object_or_404, reverse, redirect
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from .permissions import IsHostOrJoinableOnly
from .serializers import RoomSerializer, RoomRetrieveSerializer
from .models import Room
import logging


class RoomView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = RoomRetrieveSerializer
    queryset = Room.objects.all()
    lookup_field = "code"
    permission_classes = [IsHostOrJoinableOnly]

    def delete(self, request, *args, **kwargs):
        res = self.destroy(request, *args, **kwargs)
        request.session.flush()
        return res

    def get(self, request, code, *args, **kwargs):
        if Room.objects.filter(code=code).exists():
            request.session["code"] = code

        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # TODO: ADD UNJOIN


class RoomCreateView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
):
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

        if not request.session.exists(request.session.session_key):
            request.session.create()

        res = self.create(request, *args, **kwargs)
        request.session["code"] = res.data["code"]
        # return res
        return redirect(to=reverse("spotify authorization"))
