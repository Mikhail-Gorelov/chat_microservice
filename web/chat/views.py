import logging
import redis
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from pyparsing import unicode
from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from chat.models import Message
from main.models import UserData
from main.pagination import BaseCursorPagination, BasePageNumberPagination
from main.services import MainService

from . import models, serializers
from .authentication import ExampleAuthentication
from .serializers import ChatInitSerializer, ChatShortInfoSerializer
from .services import ChatService
from rest_framework.decorators import api_view
import json

logger = logging.getLogger(__name__)

redis_instance = redis.StrictRedis(host='redis', port='6379', db=0)


# проблемы с подключение, нужно понять как подключать/ подключить бд через настройки


class ManageRedisItems(GenericAPIView):
    serializer_class = serializers.RedisSerializer

    def get(self, request):
        items = {}
        count = 0
        for key in redis_instance.keys("*"):
            items[key.decode("utf-8")] = redis_instance.get(key)
            count += 1
        response = {
            'count': count,
            'msg': f"Found {count} items.",
            'items': items
        }
        return Response(response, status=200)

    def post(self, request):
        item = self.get_serializer(data=request.data)
        item.is_valid(raise_exception=True)
        item.save()
        key = item.data['key']
        value = item.data['value']
        redis_instance.set(key, value)
        response = {
            'msg': f"{key} successfully set to {value}"
        }
        return Response(response, 201)


class ManageRedisItem(GenericAPIView):
    serializer_class = serializers.RedisSerializer

    def get(self, request, **kwargs):
        if kwargs['key']:
            value = redis_instance.get(kwargs['key'])
            if value:
                response = {
                    'key': kwargs['key'],
                    'value': value,
                    'msg': 'success'
                }
                return Response(response, status=200)
            else:
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'msg': 'Not found'
                }
                return Response(response, status=404)

    def put(self, request, **kwargs):
        if kwargs['key']:
            item = serializers.RedisUpdateSerializer(data=request.data)
            item.is_valid(raise_exception=True)
            item.save()
            new_value = item.data['value']
            value = redis_instance.get(kwargs['key'])
            if value:
                redis_instance.set(kwargs['key'], new_value)
                response = {
                    'key': kwargs['key'],
                    'value': value,
                    'msg': f"Successfully updated {kwargs['key']}"
                }
                return Response(response, status=200)
            else:
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'msg': 'Not found'
                }
                return Response(response, status=404)

    def delete(self, request, **kwargs):
        if kwargs['key']:
            result = redis_instance.delete(kwargs['key'])
            if result == 1:
                response = {
                    'msg': f"{kwargs['key']} successfully deleted"
                }
                return Response(response, status=404)
            else:
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'msg': 'Not found'
                }
                return Response(response, status=404)


class LastMessagesView(ListAPIView):
    serializer_class = serializers.MessageSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Message.objects.all().order_by("-id")[:10]


class RestAndWebsocketView(GenericAPIView):
    serializer_class = serializers.RestAndWebsocketSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TestUserChatView(GenericAPIView):
    serializer_class = serializers.UserChatSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserChatView(ListAPIView):
    serializer_class = serializers.ChatListSerializer
    pagination_class = BasePageNumberPagination
    permission_classes = (AllowAny,)

    def get_queryset(self):
        user_data = ChatService.get_or_set_user_jwt(self.request.COOKIES.get(settings.JWT_COOKIE_NAME))
        self.user = UserData(**user_data)
        return ChatService.get_last_message_from_chat(user_id=self.user.id)

    def get_serializer_context(self):
        context = super(UserChatView, self).get_serializer_context()
        context['user_data'] = ChatService.get_chat_contacts_data(self.user.id, self.request)
        return context


class MessageChatView(ListAPIView):
    serializer_class = serializers.MessageListSerializer
    pagination_class = BasePageNumberPagination
    permission_classes = (AllowAny,)

    # вот здесь должна быть правка о том, что именно определённые письма выводятся
    # пока хардкодим, смотрим на что-то подобное из блога
    def get_queryset(self):
        return ChatService.get_messages_in_chat(chat=self.kwargs.get("chat_id"))

    def get_template_name(self):
        return 'chat/includes/messages.html'


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChatSerializerCheck
    pagination_class = BasePageNumberPagination
    http_method_names = ('post', 'put', 'delete')
    permission_classes = (AllowAny,)
    parser_classes = (FormParser, MultiPartParser)

    def get_queryset(self):
        return models.Chat.objects.all()


class LastChatMessage(ListAPIView):
    serializer_class = serializers.MessageSerializer
    permission_classes = (AllowAny,)
    pagination_class = BasePageNumberPagination

    def get_queryset(self):
        return ChatService.get_messages_in_chat(chat=self.kwargs.get("chat_id")).order_by("-id")[:1]


class ChatInitView(GenericAPIView):
    template_name = "chat/init.html"
    serializer_class = ChatInitSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class ChatShortInfoView(GenericAPIView):
    serializer_class = ChatShortInfoSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)
