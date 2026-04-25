from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/cozinha/$', consumers.CozinhaConsumer.as_asgi()),
]
