from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user: the email is unique, we log in with it.
    We'll leave the username field (it needs to be AbstractUser), but we can hide it in forms.
    """

    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username