import logging
import os

import redis
import uuid
from django.conf import settings
from django.core.cache import cache
from django.http import FileResponse
from django.shortcuts import render
from pyparsing import unicode
from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .choices import ChatStatus
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
        context['user'] = self.user
        return context


class MessageChatView(ListAPIView):
    serializer_class = serializers.MessageListSerializer
    pagination_class = BasePageNumberPagination
    permission_classes = (AllowAny,)

    # вот здесь должна быть правка о том, что именно определённые письма выводятся
    # пока хардкодим, смотрим на что-то подобное из блога
    def get_queryset(self):
        return ChatService.get_messages_in_chat(chat=self.kwargs.get("chat_id")).order_by("-id")

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


class UpdateFileView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.FileUploadSerializer
    queryset = models.Chat.objects.filter(status=ChatStatus.OPEN)
    parser_classes = (MultiPartParser,)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.kwargs['chat_id'])
        return obj

    def post(self, request, chat_id):
        serializer = self.get_serializer(data=request.data, instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DownloadFileView(GenericAPIView):
    queryset = models.FileMessage.objects.all()
    permission_classes = (AllowAny,)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(message=self.message_filter)
        return obj

    def get(self, request, message_id):
        self.message_filter = message_id
        obj = self.get_object()
        file_path = os.path.join(settings.MEDIA_ROOT, models.file_upload_to(obj, ""))
        return FileResponse(open(file_path, 'rb'))
