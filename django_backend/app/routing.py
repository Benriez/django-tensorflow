from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live/$', consumers.LiveViewConsumer.as_asgi()),
    re_path(r'', consumers.LiveViewConsumer.as_asgi()),
    #re_path(r'ws/client/$', consumers.ClientConsumer.as_asgi()),
]