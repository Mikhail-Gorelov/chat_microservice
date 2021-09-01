from django.contrib import admin
from . import models


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    list_display = ('username',)


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'date')
