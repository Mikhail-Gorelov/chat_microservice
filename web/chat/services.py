from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST

from main.services import MainService
from . import models


class ChatService:

    @staticmethod
    def add_users_to_chat(users: list, chat):
        objs = (models.UserChat(user_id=user, chat=chat) for user in users)
        models.UserChat.objects.bulk_create(objs)
        # for user in users:
        #     models.UserChat.objects.create(user_id=user, chat=chat)

    @staticmethod
    def get_user_chats(user_id: int):
        return models.Chat.objects.filter(user_chats__user_id=user_id)

    @staticmethod
    def get_messages_in_chat(chat: int):
        return models.Message.objects.filter(chat=chat)

    @staticmethod
    def get_all_chats():
        return models.Chat.objects.all()

    @staticmethod
    def validate_user_jwt(jwt: str, request):
        url = '/jwt/callback/'
        service = MainService(request=request, url=url)
        response = service.service_response(method="post", data={"auth": jwt})
        if response.status_code == HTTP_400_BAD_REQUEST:
            raise ValidationError(response.data)
        print(response.data)
        return response.data
