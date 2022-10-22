import json
import asyncio
import time
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
from playwright.async_api import async_playwright

from .models import Images




class ScraperViewConsumer(AsyncWebsocketConsumer):
    group_name = "scraper"
    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave group
        print('disconnected')
    
    async def receive(self, text_data):
        # Receive data from WebSocket
        data_json = json.loads(text_data)
        async with async_playwright() as playwright:
            chromium = playwright.chromium # or "firefox" or "webkit".
            browser = await chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto("https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=2&adm=00232070&app=makler")
            # other actions...
            
            #fill out external form
            await page.click('button:has-text("Alle akzeptieren")')
            await page.locator('[data-placeholder="Geburtsdatum"]').fill(data_json['birthdate'])
            await page.locator('[data-placeholder="Vorname"]').fill(data_json['vorname'])
            await page.click('button:has-text("Beitrag berechnen")')
    
            price_euro = await page.locator(".euro").inner_text()
            price_cents = await page.locator(".cent").inner_text()
            date = await page.locator('[data-placeholder="Versicherungsbeginn"]').input_value()
            str_price = price_euro + price_cents

            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'get_personal_offer',
                    'data': {
                        'message': 'Beitrag',
                        'price': str_price,
                        'date': date
                    }
                }
            )
            
            await page.click('button:has-text("Jetzt abschließen")')
            
            # step 2
            if data_json["anrede"] == "Herr":
                # await page.locator('input[value=Herr]')
                await page.click('#mat-radio-2')

            else:
                await page.click('#mat-radio-3')
            
            await page.locator('[data-placeholder="Name"]').fill(data_json['nachname'])
            await page.click('button:has-text("Weiter")')

            # step 3
            await page.locator('[data-placeholder="PLZ"]').fill(data_json['plz'])
            await page.locator('[data-placeholder="Straße"]').fill(data_json['strasse'])
            #await page.pause()

            await browser.close()

    async def get_personal_offer(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))



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
    
