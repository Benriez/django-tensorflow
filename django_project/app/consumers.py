import json
import asyncio
import time
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .models import Images


class LiveViewConsumer(AsyncWebsocketConsumer):
    group_name = "live_view"

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

        # Send data to group     
        if message == "start": 
            #get first image  
            image = await sync_to_async(Images.objects.get, thread_sensitive=True)(id=1) 
            print('url', image.file.url)
            # await self.channel_layer.group_send(
            #     self.group_name,
            #     {
            #         'type': 'client_server',
            #         'data': {
            #             'message': url, 
            #         }
            #     }
            # )


    async def client_server(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))
    


@sync_to_async
def _get_image():
    image = Images.objects.filter(seen=False).first()
    print(image.file.url)
    x = [creator for creator in image]
    return x


# @sync_to_async
# def get_image():
#     img = Images.objects.filter(seen=False).first()
#     #img.displayed = True
#     img.save()
#     return img




# class ClientConsumer(AsyncWebsocketConsumer):
#     group_name = "live_view"

#     async def connect(self):
#         # Joining group
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave group
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         # Receive data from WebSocket
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         print(message)
#         # Print message that receive from Websocket

#         # Send data to group
#         await self.channel_layer.group_send(
#             self.group_name,
#             {
#                 'type': 'system_load',
#                 'data': {
#                     'cpu_percent': 0,  # initial value for cpu and ram set to 0
#                     'ram_percent': 0
#                 }
#             }
#         )

#     async def system_load(self, event):
#         # Receive data from group
#         await self.send(text_data=json.dumps(event['data']))