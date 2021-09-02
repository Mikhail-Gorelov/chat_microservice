from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . import models, serializers
from django.utils import timezone
from urllib.parse import parse_qs


def parse_query_string(query_string):
    return parse_qs(query_string)


class AsyncChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_last_messages(self):
        queryset = models.Message.objects.all().order_by("-id").values()[:10]
        for i in queryset:
            i["date"] = i["date"].strftime("%d-%m-%Y %H:%M:%S")
        return list(queryset)
        # return models.Message.objects.all().order_by("-id").values()[:10]

    async def connect(self):
        # print(self.scope)
        self.username = parse_query_string(self.scope['query_string'].decode("utf-8")).get("username")[0]
        # TODO: проверить на наличие username, если нет, то self.close
        print(self.username)

        self.room = "general_room"
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.room, {
            "type": "fetch.messages",
            "data": {},
        })
        await self.channel_layer.group_send(self.room, {
            "type": "user.connect",
            "data": {"username": self.username},
        })
        # serializer = await sync_to_async(serializers.MessageSerializer, thread_sensitive=False)(instance=queryset, many=True)
        # print(serializer)
        # for i in await :
        #     await self.channel_layer.group_send(self.room, {
        #         "type": "chat.message",
        #         "data": i,
        #     })
        # await self.accept("username")  # как я понял здесь где-то должен лежать юзер self.scope['url_route']['kwargs']
        # здесь вызвать group_send и забрать 10 последних сообщений из бд
        # await self.close()

    def create_author(self, username="mikell"):
        return models.Author.objects.create(username=username)

    def create_message(self, content, date):
        return models.Message.objects.create(content=content, date=date, author=self.create_author())

    async def new_message(self, data):
        # сохранять сообщения в бд
        print(data)
        await self.channel_layer.group_send(self.room, {
            "type": "chat.message",
            "data": data,
        })
        await database_sync_to_async(self.create_message)(data.get("message"), timezone.now())

    async def chat_message(self, event: dict):
        # print("chat.message", event)
        data = event.get("data")
        await self.send_json(content=data)

    async def fetch_messages(self, event: dict):
        print("fetch.messages", event)
        # queryset = await self.get_last_messages()
        # data = await list(queryset)
        for i in await self.get_last_messages():
            i["type"] = event["type"]
            await self.send_json(content=i)
        # await self.send_json(content=data)

    async def user_connect(self, event: dict):
        await self.send_json(content=event)

    commands = {
        "new_message": new_message,
        "check_online_users": connect,
    }

    async def receive_json(self, content: dict, **kwargs):
        await self.commands[content["command"]](self, content)
