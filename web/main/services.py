from django.conf import settings
from microservice_request.services import MicroServiceConnect, ConnectionService
from . import models


class MainService(ConnectionService):
    service = settings.BLOG_API_URL
