import os
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from playwright.async_api import async_playwright
from PIL import Image



from .models import Images

email = "admin@mail.com"


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

        # if data_json['message'] =="client-connected":
        #     async with async_playwright() as playwright:
        #         chromium = playwright.webkit # or "firefox" or "webkit".
        #         browser = await chromium.launch(headless=True)
        #         page = await browser.new_page()
        #         await page.goto("https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=2&adm=00232070&app=makler")
        #         # other actions...
                
        #         #fill out external form
        #         await page.click('button:has-text("Alle akzeptieren")')
        #         await page.locator('[data-placeholder="Geburtsdatum"]').fill(data_json['birthdate'])
        #         await page.locator('[data-placeholder="Vorname"]').fill(data_json['vorname'])
        #         await page.click('button:has-text("Beitrag berechnen")')
        
        #         price_euro = await page.locator(".euro").inner_text()
        #         price_cents = await page.locator(".cent").inner_text()
        #         date = await page.locator('[data-placeholder="Versicherungsbeginn"]').input_value()
        #         str_price = price_euro + price_cents

                
        #         await self.channel_layer.group_send(
        #             self.group_name,
        #             {
        #                 'type': 'get_personal_offer',
        #                 'data': {
        #                     'message': 'Beitrag',
        #                     'price': str_price,
        #                     'date': date
        #                 }
        #             }
        #         )
                
        #         await page.click('button:has-text("Jetzt abschließen")')
                
        #         # step 2
        #         if data_json["anrede"] == "Herr":
        #             # await page.locator('input[value=Herr]')
        #             await page.click('#mat-radio-2')

        #         else:
        #             await page.click('#mat-radio-3')
                
        #         await page.locator('[data-placeholder="Name"]').fill(data_json['nachname'])
        #         await page.click('button:has-text("Weiter")')

        #         # step 3
        #         await page.locator('[data-placeholder="PLZ"]').fill(data_json['plz'])
        #         await page.locator('[data-placeholder="Straße"]').fill(data_json['strasse'])
        #         await page.locator('[data-placeholder="Hausnummer"]').fill(data_json['hausnr'])

        #         await page.click('mat-checkbox')
        #         await page.locator('[data-placeholder="E-Mail-Adresse"]').fill(email)
        #         await page.locator('button:has-text("Weiter")').hover()
        #         await page.click('button:has-text("Weiter")')

        #         #step 4
        #         await page.locator('[data-placeholder="IBAN"]').fill(data_json['iban'])
        #         await page.click('.mat-checkbox-inner-container')
        #         await page.locator('button[type="submit"]').hover()
        #         await page.click('button[type="submit"]')
        #         #await page.pause()

        #         #step 5
        #         async with page.expect_popup() as popup:
        #             await page.click('baf-link', modifiers=["Alt",])

        #         loader_page = await popup.value
        #         await loader_page.wait_for_url("blob:**")
        #         await loader_page.set_viewport_size({"width": 2480, "height": 3496})

        #         print_pages = 29
        #         image_list =[]
        #         for p in range(print_pages):
        #             await loader_page.screenshot(path="screenshot"+str(p)+".png", full_page=True)
        #             await loader_page.mouse.wheel(0, 3496)
        #             image = Image.open(r'screenshot'+str(p)+'.png')
        #             im_con = image.convert('RGB')
        #             image_list.append(im_con)
                
        #         im_con.save('./media/pdfs/Mein_Angebot.pdf', save_all=True, append_images=image_list)

        #         await self.channel_layer.group_send(
        #             self.group_name,
        #             {
        #                 'type': 'serve_personal_offer',
        #                 'data': {
        #                     'message': 'Done'
        #                 }
        #             }
        #         )

                
        #         #await page.pause()
        #         await page.locator(".mat-checkbox-inner-container").first.click()
        #         await page.locator("#mat-checkbox-5 > .mat-checkbox-layout > .mat-checkbox-inner-container").click()
        #         await page.locator("#mat-checkbox-4 > .mat-checkbox-layout > .mat-checkbox-inner-container").click()
                
        #         # Final step klick "weiter"
        #         await page.pause()
        #         await browser.close()            
                
        #         for p in range(print_pages):
        #             os.remove(r'screenshot'+str(p)+'.png')

        # if data_json['message'] == "get_zahnzusatz_pricelist":
        #     print('get_zahnzusatz_pricelist')
        #     async with async_playwright() as playwright:
        #         chromium = playwright.webkit # or "firefox" or "webkit".
        #         browser = await chromium.launch(headless=False)
        #         page = await browser.new_page()
        #         await page.goto("https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=1&app=makler&ADM=00232070")
        #         # other actions...
                
        #         #fill out external form
        #         await page.get_by_test_id("uc-save-button").click()
        #         await page.get_by_label("Geburtsdatum").fill(data_json['birthdate'])
        #         await page.keyboard.press('Tab')
        #         await page.get_by_role("button", name="Beitrag berechnen").click()


        #         await page.pause()
        




    async def get_personal_offer(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_personal_offer(self, event):
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
    
