from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions


class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the username and password
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if not username or not password:
            raise exceptions.AuthenticationFailed('No credentials provided.')

        credentials = {get_user_model().USERNAME_FIELD: username, 'password': password}

        user = authenticate(**credentials)

        if user is None:
            raise exceptions.AuthenticationFailed('Invalid username/password.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, None)  # authentication successful
