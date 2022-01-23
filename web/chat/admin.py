from django.contrib import admin

from . import models


class UserChatInline(admin.StackedInline):
    model = models.UserChat
    extra = 0


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'date')


@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    inlines = (UserChatInline,)


@admin.register(models.UserChat)
class UserChatAdmin(admin.ModelAdmin):
    pass
