import logging
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from . import services
from . import serializers

logger = logging.getLogger(__name__)

# from django.shortcuts import render
#
#
# def index(request):
#     return render(request, 'chat/index.html', {})
#
#
# def username(request, room_name):
#     return render(request, 'chat/index.html', {
#         'username': username
#     })
