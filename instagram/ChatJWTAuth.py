from channels.db import database_sync_to_async
from django.http import request
from core.models import User
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
import jwt
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError
from django.conf import settings

@database_sync_to_async
def authenticate(request):
    # auth_data = authentication.get_authorization_header(request)
    auth_data = request["headers"][4][1]
    
    if not auth_data:
        return None
    
    prefix, token = auth_data.decode('utf-8').split(' ')

    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        try:
            user = User.objects.get(id=payload["user_id"])
        except:
            raise AuthenticationFailed('Invalid Token')
        return user
        
    except jwt.ExpiredSignatureError as e:
        raise ValidationError({"error": ["Token has Expired"]})

    except jwt.exceptions.DecodeError as e:
        raise AuthenticationFailed('Invalid Token')

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).

        scope['user'] = await authenticate(scope)

        return await self.app(scope, receive, send)