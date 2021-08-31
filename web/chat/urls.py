from django.urls import path
from rest_framework.routers import DefaultRouter
from main.views import TemplateAPIView
from . import views

app_name = 'chat'

router = DefaultRouter()

urlpatterns = [
    path('', TemplateAPIView.as_view(template_name='chat/index.html'), name='index'),
]

urlpatterns += router.urls
