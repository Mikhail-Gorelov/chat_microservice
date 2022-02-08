from datetime import datetime
from urllib.parse import parse_qs
from django.conf import settings
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.cache import cache
import pytz
from django.utils import timezone, dateformat
from main.models import ChatDataId, UserData
from main.services import MainService

from . import models, serializers
from .services import AsyncChatService, ChatService


def parse_query_string(query_string):
    return parse_qs(query_string)


class AsyncChatConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    def get_last_message_serializer(self):
        queryset = models.Message.objects.all().order_by("-id")[:1]
        serializer = serializers.MessageSerializer(instance=queryset, many=True)
        return list(serializer.data)

    async def connect(self):
        self.user = self.scope['user']
        self.redis = settings.REDIS_DATABASE
        await self.init_user_chat()
        await self.accept()
        await self.set_user_online()

    async def set_user_online(self):
        self.redis.hmset(str(self.user["id"]), {
            "status": "online",
            "last_seen": "None",
        })
        self.redis.bgsave()

    async def set_user_offline(self):
        date = datetime.fromisoformat(str(timezone.now())).replace(tzinfo=None).replace(microsecond=0)
        date_time = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        self.redis.hmset(str(self.user["id"]), {
            "status": "offline",
            "last_seen": str(date_time + pytz.timezone(settings.TIME_ZONE).utcoffset(date_time)),
        })
        self.redis.bgsave()

    async def init_user_chat(self):
        chat_list: list[ChatDataId] = [
            ChatDataId(data) for data in await AsyncChatService.get_chat_list(self.user["id"])
        ]
        await self.channel_layer.group_add(f"events_for_user_{self.user['id']}", self.channel_name)
        for chat in chat_list:
            await self.channel_layer.group_add(str(chat.id), self.channel_name)
        return chat_list

    async def add_chat(self, event: dict):
        data = event.get('data')
        await self.channel_layer.group_add(data['chat_id'], self.channel_name)
        data['command'] = 'add_chat'
        print(data)
        await self.send_json(content=data)

    async def disconnect(self, close_code):
        await self.set_user_offline()
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

    @database_sync_to_async
    def create_message(self, content, chat_id):
        return models.Message.objects.create(
            content=content, chat=models.Chat.objects.get(id=chat_id), author_id=self.user["id"]
        )

    async def new_message(self, data):
        message = await self.create_message(data.get("message"), data.get("chat_id"))
        data_template = await self.response_template(
            chat_id=data.get("chat_id"),
            type="chat.message",
            command="new_message",
            message_id=message.pk,
            author_id=message.author_id,
            content=message.content,
            date=str(message.date),
            has_read=message.has_read
        )
        message_count: dict = await database_sync_to_async(message.chat.count_unread_messages)(message.author_id)
        data_template["count_unread"] = message_count["count"]
        await self.channel_layer.group_send(
            data_template.get("chat_id"),
            {
                "type": data_template.get("type"),
                "data": data_template,
            }
        )

    async def response_template(self, **kwargs) -> dict:
        return {
            "chat_id": kwargs["chat_id"],
            "type": kwargs["type"],
            "data": {
                "command": kwargs.get("command"),
                "message_id": kwargs.get("message_id"),
                "author_id": kwargs.get("author_id"),
                "content": kwargs.get("content"),
                "date": kwargs.get("date"),
                "has_read": kwargs.get("has_read"),
            }
        }

    @database_sync_to_async
    def check_message_db(self, message_id):
        message = models.Message.objects.get(pk=message_id)
        message.has_read = True
        message.save()
        return message

    async def check_message(self, data):
        data_template = await self.response_template(
            chat_id=data.get("chat_id"),
            type="chat.message",
            command="check_message",
            message_id=data.get("message_id"),
        )
        await self.channel_layer.group_send(
            data_template.get("chat_id"),
            {
                "type": data_template.pop("type"),
                "data": data_template,
            }
        )
        await self.check_message_db(data.get("message_id"))

    async def chat_message(self, event: dict):
        data = event.get("data")
        data_new = await self.get_last_message_serializer()
        data.update(dict(data_new[0]))
        await self.send_json(content=data)

    async def user_connect(self, event: dict):
        await self.send_json(content=event)

    commands = {
        "new_message": new_message,
        "check_message": check_message,
    }

    async def receive_json(self, content: dict, **kwargs):
        await self.commands[content["command"]](self, content)
