from django.db import models
from random import choices

# Create your models here.

# TODO: find better way to obtain random-like primary key
#      to avoid generating key that already exists
def get_random_code() -> str:
    numbers = [str(n) for n in range(10)]
    return "".join(choices(numbers, k=6))


class Room(models.Model):
    code = models.CharField(max_length=6, primary_key=True, default=get_random_code)
    host = models.CharField(max_length=16)
    votes_to_skip = models.IntegerField()
    max_capacity = models.IntegerField()
    user_can_pause = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
