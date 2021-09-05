from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . import models
from urllib.parse import parse_qs


def parse_query_string(query_string):
    return parse_qs(query_string)


class AsyncChatConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect_user(self):
        await self.update_user_status(self.username, 'online')

    async def websocket_disconnect_user(self):
        await self.update_user_status(self.username, 'offline')

    @database_sync_to_async
    def update_user_status(self, user, status):
        return models.Author.objects.filter(username=user).update(status=status)

    async def connect(self):
        self.username = parse_query_string(self.scope['query_string'].decode("utf-8")).get("username")[0]
        if self.username == '':
            await self.close()
        self.author_obj = await self.create_author()
        await self.websocket_connect_user()
        self.room = "general_room"
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.room, {
            "type": "user.connect",
            "data": {"username": self.username},
        })

    async def disconnect(self, close_code):
        await self.websocket_disconnect_user()
        await self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )

    @database_sync_to_async
    def create_author(self):
        return models.Author.objects.get_or_create(username=self.username)[0]

    @database_sync_to_async
    def create_message(self, content):
        return models.Message.objects.create(content=content, author=self.author_obj)

    async def new_message(self, data):
        await self.channel_layer.group_send(self.room, {
            "type": "chat.message",
            "data": data,
        })
        await self.create_message(data.get("message"))

    async def chat_message(self, event: dict):
        data = event.get("data")
        await self.send_json(content=data)

    async def user_connect(self, event: dict):
        await self.send_json(content=event)

    commands = {
        "new_message": new_message,
        "check_online_users": connect,
    }

    async def receive_json(self, content: dict, **kwargs):
        await self.commands[content["command"]](self, content)
