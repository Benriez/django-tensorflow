import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from system import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),     # For Http Connection
    "websocket": AuthMiddlewareStack(   # For Websocket Connection
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})