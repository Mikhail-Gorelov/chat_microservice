from django.conf import settings
from microservice_request.services import ConnectionService, MicroServiceConnect

from . import models


class MainService(ConnectionService):
    service = settings.BLOG_API_URL
