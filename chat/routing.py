# chat/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, include
from . import consumer

websocket_urlpatterns = [
  path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumer.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns,

            )
        )
    ),
})
