import json
import asyncio
import time
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .models import Images


class ScraperViewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave group
        print('disconnected')
    
    async def receive(self, text_data):
        # Receive data from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print('message:', message)







class LiveViewConsumer(AsyncWebsocketConsumer):
    group_name = "live_view"

    async def connect(self):
        # Joining group
        print('liveviewConsumer connect')
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        print('liveviewConsumer disconnect')
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive data from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']



        if message == "liveview-server connected": 
            pass

        if message == "displacement-x": 
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'client_server',
                    'data': {
                        'message': 'displacement-x',
                        'value': text_data_json['value'] 
                    }
                }
            )

        if message == "displacement-y": 
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'client_server',
                    'data': {
                        'message': 'displacement-y',
                        'value': text_data_json['value'] 
                    }
                }
            )

        if message == "client-connected": 
            deviceID = text_data_json['deviceID']
            print('deviceID ', deviceID)

   
        # Send data to group     
        if message == "start": 
    
            url = await get_next_image()
            if url:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'client_server',
                        'data': {
                            'message': 'start',
                            'src': url 
                        }
                    }
                )
        
        if message == "reset":
            await reset()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'client_server',
                    'data': {
                        'message': 'reset', 
                    }
                }
            )


    async def client_server(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))
    


#-----------------------------------------------------------------------------------------
@sync_to_async
def get_next_image():
    try:
        img = Images.objects.all().filter(seen=False).filter(displayed=False).first()
        img.displayed = True
        img.seen = True
        img.save()

        next = img.file.url
        #next = img      
    except:
        next = None


    return next


@sync_to_async
def reset(): 
    imgs = Images.objects.all()

    for i in imgs:
        i.displayed = False
        i.seen = False
        i.save()
    
