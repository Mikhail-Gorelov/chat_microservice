from django.urls import path
from rest_framework.routers import DefaultRouter
from main.views import TemplateAPIView
from chat.views import LastMessagesView, ListAuthorView

app_name = 'chat'

router = DefaultRouter()

urlpatterns = [
    path('', TemplateAPIView.as_view(template_name='chat/index.html'), name='index'),
    path('last-messages/', LastMessagesView.as_view(), name="last-messages"),
    path('author-status/', ListAuthorView.as_view(), name="author-status"),
]

urlpatterns += router.urls
