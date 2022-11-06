import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import app.routing
import system.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')

websocket_urls = []
websocket_urls.extend(app.routing.websocket_urlpatterns)
websocket_urls.extend(system.routing.websocket_urlpatterns)


application = ProtocolTypeRouter({
    "http": get_asgi_application(),     # For Http Connection
    "websocket": AuthMiddlewareStack(   # For Websocket Connection
        URLRouter(
            websocket_urls
        )
    ),
})