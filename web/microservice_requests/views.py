import logging
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth import views as auth_views
from main.services import MainService
from . import services
from . import serializers

logger = logging.getLogger(__name__)


# Create your views here.

class CategoriesListView(GenericAPIView):
    serializer_class = serializers.PostCategoryInBlog
    permission_classes = (AllowAny,)
    swagger_schema = None

    def get(self, request):
        service = MainService(request=request, url='/categories/')
        response = service.service_response(method="get")
        print(response.data)
        return Response(response.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryChangeView(GenericAPIView):
    serializer_class = serializers.PostCategoryInBlog
    permission_classes = (AllowAny,)
    swagger_schema = None

    # TODO: удаляет, но с ошибкой - вопрос почему
    def delete(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        service = MainService(request=request, url=f'/categories/{slug}/')
        response = service.service_response(method="delete")
        print(response.data)
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        service = MainService(request=request, url=f'/categories/{slug}/')
        response = service.service_response(method="put", data=request.data)
        return Response(response.data)


class LoginView(auth_views.LoginView):
    serializer_class = serializers.LoginSerializer
    # authentication_classes = (ExampleAuthentication,)
    swagger_schema = None


class ChatRegisterView(GenericAPIView):
    serializer_class = serializers.RegisterUserInBlog
    permission_classes = (AllowAny,)
    swagger_schema = None

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
