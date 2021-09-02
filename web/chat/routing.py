from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # path(r'ws/chat/(?P<username>\w+)/$', consumers.AsyncChatConsumer.as_asgi()),
    path('ws/chat/', consumers.AsyncChatConsumer.as_asgi()),
]
