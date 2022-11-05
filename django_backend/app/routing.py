from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/scraper/$', consumers.ScraperViewConsumer.as_asgi()),
    re_path(r'ws/extra-scraper/$', consumers.ExtraViewConsumer.as_asgi())
    #re_path(r'ws/client/$', consumers.ClientConsumer.as_asgi()),
]