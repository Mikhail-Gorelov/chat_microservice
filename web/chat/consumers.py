from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import UserData, ChatDataId
from main.services import MainService
from . import models, serializers
from urllib.parse import parse_qs
from django.core.cache import cache
from .services import ChatService, AsyncChatService


def parse_query_string(query_string):
    return parse_qs(query_string)


class AsyncChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def check_chat_status(self, room_name):
        try:
            status = models.Chat.objects.get(name=room_name).status
            if status == 0:
                raise PermissionError({"room": "wrong room"})
        except Exception:  # bad definition
            status = None
        return room_name

    @database_sync_to_async
    def get_last_message_serializer(self):
        queryset = models.Message.objects.all().order_by("-id")[:1]
        serializer = serializers.MessageSerializer(instance=queryset, many=True)
        return list(serializer.data)

    async def connect(self):
        self.user = self.scope['user']
        await self.init_user_chat()
        await self.accept()

    async def init_user_chat(self):
        chat_list: list[ChatDataId] = [
            ChatDataId(data) for data in await AsyncChatService.get_chat_list(self.user['id'])
        ]
        await self.channel_layer.group_add(f"events_for_user_{self.user['id']}", self.channel_name)
        # print(f"events_for_user_{self.user['id']}")
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
        pass
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

    @database_sync_to_async
    def create_message(self, content, chat_id):
        return models.Message.objects.create(
            content=content, chat=models.Chat.objects.get(id=chat_id), author_id=self.user['id']
        )

    async def new_message(self, data):
        await self.channel_layer.group_send(
            data.get('chat_id'),
            {
                "type": "chat.message",
                "data": data,
            },
        )
        await self.create_message(data.get("message"), data.get('chat_id'))

    async def chat_message(self, event: dict):
        data = event.get("data")
        data_new = await self.get_last_message_serializer()
        data.update(dict(data_new[0]))
        await self.send_json(content=data)

    async def user_connect(self, event: dict):
        await self.send_json(content=event)

    commands = {
        "new_message": new_message,
        "check_online_users": connect,
    }

    async def receive_json(self, content: dict, **kwargs):
        await self.commands[content["command"]](self, content)
