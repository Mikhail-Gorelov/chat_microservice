from django.conf import settings
from microservice_request.services import MicroServiceConnect, ConnectionService
from . import models


class MainService(MicroServiceConnect):
    service = settings.BLOG_API_URL
