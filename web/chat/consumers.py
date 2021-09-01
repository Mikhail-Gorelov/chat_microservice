from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . import models
from django.utils import timezone


class AsyncChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print(self.scope["user"])
        self.room = "general_room"
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        # здесь вызвать group_send и забрать 10 последних сообщений из бд
        # await self.close()

    def create_message(self, content, date):
        return models.Message.objects.create(content=content, date=date)

    # def save_message(self):
    #     return models.Message.objects.save()

    async def new_message(self, data):
        # сохранять сообщения в бд
        print(data)
        await self.channel_layer.group_send(self.room, {
            "type": "chat.message",
            "data": data,
        })
        await database_sync_to_async(self.create_message)(data.get("message"), timezone.now())
        # await database_sync_to_async(self.save_message)()

    async def chat_message(self, event: dict):
        print("chat.message", event)
        data = event.get("data")
        await self.send_json(content=data)

    commands = {
        "new_message": new_message,
    }

    async def receive_json(self, content: dict, **kwargs):
        await self.commands[content["command"]](self, content)
