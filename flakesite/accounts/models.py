from django.contrib.auth.models import AbstractUser
from django.db import models

from flake_app.models import Device

# TODO: Evaluate if this is better done with an additional model such as 'FlakeUser' in flake_app, tied to the user model with
# a one-to-one key.
class User(AbstractUser):
    current_device = models.ForeignKey(Device, on_delete = models.SET_NULL, null = True)