from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live/$', consumers.LiveViewConsumer.as_asgi()),
    re_path(r'ws/2/$', consumers.LiveViewConsumer.as_asgi()),
    re_path(r'ws/3/$', consumers.LiveViewConsumer.as_asgi()),
]