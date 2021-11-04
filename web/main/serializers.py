import pytz
from rest_framework import serializers
from chat.services import ChatService


class SetTimeZoneSerializer(serializers.Serializer):
    timezone = serializers.ChoiceField(choices=pytz.common_timezones)
