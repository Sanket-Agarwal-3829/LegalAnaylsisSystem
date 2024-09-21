from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# from apps.users.managers import UserManager

class CustomUser(AbstractUser):
    pass
    # add additional fields in here

    def __str__(self):
        return self.username