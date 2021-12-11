from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from typing import NamedTuple
from uuid import uuid4
from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('Email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def full_name(self):
        return super().get_full_name()


class UserData(NamedTuple):
    id: int
    full_name: str
    image: str
    profile: str


class ChatData(NamedTuple):
    id: uuid4
    name: str
    description: str
    status: int
    date: str
    file: str
    last_message: str


class ChatDataId(NamedTuple):
    id: uuid4
