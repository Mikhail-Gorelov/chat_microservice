from rest_framework import serializers
from dj_rest_auth import serializers as auth_serializers
from main.services import MainService


class RegisterUserInBlog(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, max_length=100, required=True)
    last_name = serializers.CharField(min_length=2, max_length=100, required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    # birthday = serializers.DateField(required=True)
    gender = serializers.IntegerField()

    def save(self, **kwargs):
        print(self.validated_data)
        service = MainService(request=self.context['request'], url='/auth/sign-up/')
        validated_data = self.validated_data
        validated_data['birthday'] = "1997-11-16"
        response = service.service_response(method="post", data=validated_data)
        print(response.data)


class PostCategoryInBlog(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True, allow_unicode=True)

    def save(self, **kwargs):
        service = MainService(request=self.context['request'], url='/categories/')
        response = service.service_response(method="post", data=self.validated_data)
        print(response.data)


class LoginSerializer(auth_serializers.LoginSerializer):
    username = None
    password = serializers.CharField()
