import logging
from chat.models import Message, Author

from rest_framework.generics import ListAPIView

from chat.serializers import MessageSerializer, AuthorSerializer

logger = logging.getLogger(__name__)


class LastMessagesView(ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.select_related("author").all().order_by("-id")[:10]


class ListAuthorView(ListAPIView):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return Author.objects.filter(status='online')
