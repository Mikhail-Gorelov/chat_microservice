from channels.sessions import CookieMiddleware
from chat.services import ChatService


class CookieAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        user_jwt = scope['cookies'].get('jwt-auth')
        if not user_jwt:
            return
        print(user_jwt)
        scope['user'] = ChatService.get_or_set_user_jwt(user_jwt)
        return self.app(scope, receive, send)


def AuthMiddlewareStack(inner):
    return CookieMiddleware(CookieAuthMiddleware(inner))
