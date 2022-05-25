from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse("HI")


def create_room(request):
    pass
    return HttpResponse("CreateRoom")


def join_room(request):
    return HttpResponse("JoinRoom")
