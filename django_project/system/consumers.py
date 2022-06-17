import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class SystemConsumer(AsyncWebsocketConsumer):
    group_name = settings.STREAM_SOCKET_GROUP_NAME

    async def connect(self):
        # Joining group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive data from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        # Print message that receive from Websocket

        # Send data to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'system_load',
                'data': {
                    'cpu_percent': 0,  # initial value for cpu and ram set to 0
                    'ram_percent': 0
                }
            }
        )

    async def system_load(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))