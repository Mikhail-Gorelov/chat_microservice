from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

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
    def get_last_messages_serializer(self):
        queryset = models.Message.objects.all().order_by("-id")[:10]
        serializer = serializers.MessageSerializer(instance=queryset, many=True)
        return list(serializer.data)

    async def connect(self):
        self.user = self.scope['user']
        await self.init_user_chat()
        await self.accept()
        # await self.channel_layer.group_send(self.room_group_name, {
        #     "type": "fetch.messages",
        #     "data": {},
        # })

    async def init_user_chat(self):
        chat_list: list[str] = await AsyncChatService.get_chat_list(self.user['id'])
        for chat in chat_list:
            await self.channel_layer.group_add(str(chat), self.channel_name)

    async def disconnect(self, close_code):
        pass
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

    @database_sync_to_async
    def create_message(self, content):
        return models.Message.objects.create(content=content, author_id=1)

    async def new_message(self, data):
        print("new message", data)
        # await self.channel_layer.group_send(self.room_group_name, {
        #     "type": "chat.message",
        #     "data": data,
        # })
        # await self.create_message(data.get("message"))

    async def chat_message(self, event: dict):
        print(event.get("data"))
        data = event.get("data")
        await self.send_json(content=data)

    async def fetch_messages(self, event: dict):
        print('fetch.messages', event)
        for i in await self.get_last_messages_serializer():
            i["type"] = event["type"]
            i["author_id"] = 'mike'
            await self.send_json(content=i)

    async def user_connect(self, event: dict):
        await self.send_json(content=event)

    commands = {
        "new_message": new_message,
        "check_online_users": connect,
    }

    async def receive_json(self, content: dict, **kwargs):
        print(content, kwargs)
        await self.commands[content["command"]](self, content)
