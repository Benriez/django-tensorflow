import os
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings.main')
import django
django.setup()
import app.routing

websocket_urls = []
websocket_urls.extend(app.routing.websocket_urlpatterns)


application = ProtocolTypeRouter({
    "http": get_asgi_application(),     # For Http Connection
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(   # For Websocket Connection
            URLRouter(
                websocket_urls
            )
        ),
    )
})