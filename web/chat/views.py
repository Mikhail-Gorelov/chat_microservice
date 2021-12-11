import logging
from django.conf import settings
from django.shortcuts import render
from pyparsing import unicode
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from main.pagination import BasePageNumberPagination, BaseCursorPagination
from chat.models import Message
from main.services import MainService
from .authentication import ExampleAuthentication
from .serializers import ChatInitSerializer, ChatShortInfoSerializer
from .services import ChatService
from rest_framework.generics import ListAPIView, GenericAPIView
from . import serializers
from rest_framework import viewsets, status
from django.core.cache import cache
from . import models
from main.models import UserData

logger = logging.getLogger(__name__)


class LastMessagesView(ListAPIView):
    serializer_class = serializers.MessageSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Message.objects.all().order_by("-id")[:10]


class RestAndWebsocketView(GenericAPIView):
    serializer_class = serializers.RestAndWebsocketSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TestUserChatView(GenericAPIView):
    serializer_class = serializers.UserChatSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserChatView(ListAPIView):
    serializer_class = serializers.ChatListSerializer
    pagination_class = BasePageNumberPagination

    def get_queryset(self):
        user_data = ChatService.get_or_set_user_jwt(
            self.request.COOKIES.get(settings.JWT_COOKIE_NAME)
        )
        self.user = UserData(**user_data)
        return ChatService.get_last_message_from_chat(user_id=self.user.id)

    def get_serializer_context(self):
        context = super(UserChatView, self).get_serializer_context()
        context['user_data'] = ChatService.get_chat_contacts_data(self.user.id, self.request)
        return context


class MessageChatView(ListAPIView):
    serializer_class = serializers.MessageListSerializer
    pagination_class = BaseCursorPagination

    # вот здесь должна быть правка о том, что именно определённые письма выводятся
    # пока хардкодим, смотрим на что-то подобное из блога
    def get_queryset(self):
        return ChatService.get_messages_in_chat(chat=self.kwargs.get("chat_id")).order_by("id")

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
