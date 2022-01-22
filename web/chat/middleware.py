from channels.sessions import CookieMiddleware
from chat.services import AsyncChatService


class CookieAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # user_jwt = scope['cookies'].get('jwt-auth')
        # if not user_jwt:
        #     return
        # scope['user'] = await AsyncChatService.get_user(user_jwt)
        return await self.app(scope, receive, send)


def AuthMiddlewareStack(inner):
    return CookieMiddleware(CookieAuthMiddleware(inner))
