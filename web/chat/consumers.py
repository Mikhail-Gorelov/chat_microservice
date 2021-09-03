import json
from datetime import datetime
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . import models, serializers
from django.utils import timezone
from urllib.parse import parse_qs


def parse_query_string(query_string):
    return parse_qs(query_string)


class AsyncChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_last_messages_serializer(self):
        queryset = models.Message.objects.all().order_by("-id")[:10]
        serializer = serializers.MessageSerializer(instance=queryset, many=True)
        output = json.loads(json.dumps(serializer.data))
        for i in output:
            i["date"] = datetime.strptime(i["date"], '%Y-%d-%mT%H:%M:%S.%f+03:00')
            i["date"] = i["date"].strftime("%d-%m-%Y %H:%M:%S")
        return list(output)

    async def connect(self):
        self.username = parse_query_string(self.scope['query_string'].decode("utf-8")).get("username")[0]
        if self.username == '':
            await self.close()
        self.room = "general_room"
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        await database_sync_to_async(self.create_author)()
        await self.channel_layer.group_send(self.room, {
            "type": "fetch.messages",
            "data": {},
        })
        await self.channel_layer.group_send(self.room, {
            "type": "user.connect",
            "data": {"username": self.username},
        })
        print(await self.get_last_messages_serializer())

    def create_author(self):
        return models.Author.objects.create(username=self.username)

    def create_message(self, content, date):
        return models.Message.objects.create(content=content, date=date, author=self.get_author())

    def get_author_name(self, custom_id):
        return models.Author.objects.filter(id=custom_id).values()[0].get("username")

    def get_author(self):
        return models.Author.objects.filter(username=self.username)[0]

    async def new_message(self, data):
        print(data)
        await self.channel_layer.group_send(self.room, {
            "type": "chat.message",
            "data": data,
        })
        await database_sync_to_async(self.create_message)(data.get("message"), timezone.now())

    async def chat_message(self, event: dict):
        data = event.get("data")
        await self.send_json(content=data)

    async def fetch_messages(self, event: dict):
        print("fetch.messages", event)
        for i in await self.get_last_messages_serializer():
            i["type"] = event["type"]
            custom_id = i["author_id"]
            i["author_id"] = await database_sync_to_async(self.get_author_name)(custom_id)
            await self.send_json(content=i)

    async def user_connect(self, event: dict):
        await self.send_json(content=event)

    commands = {
        "new_message": new_message,
        "check_online_users": connect,
    }

    async def receive_json(self, content: dict, **kwargs):
        await self.commands[content["command"]](self, content)
