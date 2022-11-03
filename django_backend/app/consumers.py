import os
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from playwright.async_api import async_playwright
from PIL import Image



email = "admin@mail.com"
print_pages = 29

class ScraperViewConsumer(AsyncWebsocketConsumer):
    group_name = "scraper"
    url_offer = "https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=2&adm=00232070&app=makler"
    url_extra = "https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=1&app=makler&ADM=00232070"

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

        if data_json['message'] =="client-connected":
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_offer)
                # other actions...
                
                #fill out external form
                date, str_price = await get_offer_price(page, data_json) 
                await browser.close()               
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
                
                #----------
                #await page.pause()
                # await page.locator(".mat-checkbox-inner-container").first.click()
                # await page.locator("#mat-checkbox-5 > .mat-checkbox-layout > .mat-checkbox-inner-container").click()
                # await page.locator("#mat-checkbox-4 > .mat-checkbox-layout > .mat-checkbox-inner-container").click()
                
                # Final step klick "weiter"
                # await page.pause()
                #await browser.close()            
                

        if data_json['message'] == 'beitrag-received':
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_offer)
                # other actions...
                
                #fill out external form
                await get_offer_pdf(page, data_json) 
                await browser.close() 
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'serve_personal_offer',
                        'data': {
                            'message': 'Done'
                        }
                    }
                )

        elif data_json['message'] == "get_extra_pricelist":
            async with async_playwright() as playwright:
                chromium = playwright.chromium # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)
                
                #fill out external form
                small_price, medium_price, large_price, damage_text = await get_extra_price(page, data_json)           
                await browser.close()               
                # send result back to client
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'serve_price',
                        'data': {
                            'message': 'serve_zahnzusatz_pricelist',
                            'small': small_price,
                            'medium': medium_price,
                            'large': large_price,
                            'damage_text': damage_text
                        }
                    }
                )

        elif data_json['message'] == "get_extra_offer_pdf":
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)

                await get_extra_pdf(page, data_json)
                #await page.pause()
                await browser.close() 

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'serve_price',
                        'data': {
                            'message': 'extra_done',
                        }
                    }
                )

        elif data_json['message'] == "clear-data":
            pass
   

    #-----------------------------------------------------------------------------
    #
    async def get_personal_offer(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_personal_offer(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_price(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))



#----------------------------------------------------------------------------------
#
#
async def get_offer_price(page, data_json):
    await get_offer_step1(page, data_json)
    price_euro = await page.locator(".euro").inner_text()
    price_cents = await page.locator(".cent").inner_text()
    date = await page.locator('[data-placeholder="Versicherungsbeginn"]').input_value()
    str_price = price_euro + price_cents    
    return date, str_price


async def get_extra_price(page, data_json):
    await get_extra_step1(page, data_json)

    small_price_eur = await page.locator(".euro >>nth=0").inner_text()
    small_price_cent = await page.locator(".cent >>nth=0").inner_text()
    small_price = small_price_eur + small_price_cent

    medium_price_eur = await page.locator(".euro >>nth=1").inner_text()
    medium_price_cent = await page.locator(".cent >>nth=1").inner_text()
    medium_price = medium_price_eur + medium_price_cent

    large_price_eur = await page.locator(".euro >>nth=2").inner_text()
    large_price_cent = await page.locator(".cent >>nth=2").inner_text()
    large_price = large_price_eur + large_price_cent

    await page.get_by_role("button", name="Jetzt abschließen").click()

    # get price of 2 damaged teeth
    for i in range(2):
        await page.click('#button-more-damage')

    text1_damage2 = await page.locator("li >>nth=0").inner_text()
    text2_damage2 = await page.locator("li >>nth=1").inner_text()
    text3_damage2 = await page.locator("li >>nth=2").inner_text()
    
    # get price of 3 damaged teeth
    await page.click('#button-more-damage')
    text1_damage3 = await page.locator("li >>nth=0").inner_text()
    text2_damage3 = await page.locator("li >>nth=1").inner_text()
    text3_damage3 = await page.locator("li >>nth=2").inner_text()   


    damage_text = {
        'text1_damage2':text1_damage2,
        'text2_damage2':text2_damage2,
        'text3_damage2':text3_damage2,
        'text1_damage3':text1_damage3,
        'text2_damage3':text2_damage3,
        'text3_damage3':text3_damage3

    }
    return small_price, medium_price, large_price, damage_text


async def get_offer_pdf(page, data_json):
    await get_offer_step1(page, data_json)
    await get_offer_step2(page, data_json)
    await create_pdf(page, name='personal')



async def get_extra_pdf(page, data_json):
    await get_extra_step1(page, data_json)
    await get_extra_step2(page, data_json)
    await create_pdf(page, name='Extra')
    #await page.pause()




#------------------------------------------------------------------------
# STEPS - OFFER
#

async def get_offer_step1(page, data_json):
    await page.click('button:has-text("Alle akzeptieren")')
    await page.locator('[data-placeholder="Geburtsdatum"]').fill(data_json['birthdate'])
    await page.locator('[data-placeholder="Vorname"]').fill(data_json['vorname'])
    await page.click('button:has-text("Beitrag berechnen")')

async def get_offer_step2(page, data_json):
    # page 2
    await page.click('button:has-text("Jetzt abschließen")')
    if data_json["anrede"] == "Herr":
        await page.click('#mat-radio-2') # Herr
    else:
        await page.click('#mat-radio-3') # Frau
    
    await page.locator('[data-placeholder="Name"]').fill(data_json['nachname'])
    await page.click('button:has-text("Weiter")')

    # page 3
    await page.locator('[data-placeholder="PLZ"]').fill(data_json['plz'])
    await page.locator('[data-placeholder="Straße"]').fill(data_json['strasse'])
    await page.locator('[data-placeholder="Hausnummer"]').fill(data_json['hausnr'])

    await page.click('mat-checkbox')
    await page.locator('[data-placeholder="E-Mail-Adresse"]').fill(email)
    await page.locator('button:has-text("Weiter")').hover()
    await page.click('button:has-text("Weiter")')

    # page 4
    await page.locator('[data-placeholder="IBAN"]').fill(data_json['iban'])
    await page.click('.mat-checkbox-inner-container')
    await page.locator('button[type="submit"]').hover()
    await page.click('button[type="submit"]')


#------------------------------------------------------------------------
# STEPS - EXTRA
#
async def get_extra_step1(page, data_json):
    await page.get_by_test_id("uc-save-button").click()
    await page.get_by_label("Geburtsdatum").fill(data_json['birthdate'])
    await page.keyboard.press('Tab')
    await page.get_by_role("button", name="Beitrag berechnen").click()


async def get_extra_step2(page, data_json):
    extra_behandlung = data_json['extra_behandlung']
    missing_teeth = data_json['missing_teeth']
    current_contract = data_json['current_contract']

    if data_json['selection'] == 0:
        await page.locator("oa-tarif-container-neu:has-text(\"Mehr Zahn 80\") a").click()
    elif data_json['selection'] == 1:
        pass # is selected by default
    elif data_json['selection'] == 2:
        await page.locator("oa-tarif-container-neu:has-text(\"Mehr Zahn 100\") a").click()

    await page.get_by_role("button", name="Jetzt abschließen").click()
    if data_json["anrede"] == "Herr":
        await page.click('#mat-radio-8') # Herr
    else:
        await page.click('#mat-radio-9') # Frau

    await page.locator('[data-placeholder="Vorname"]').fill(data_json['vorname'])
    await page.locator('[data-placeholder="Name"]').fill(data_json['nachname'])

    
    if extra_behandlung == True:
        await page.click('#mat-radio-4')
    else:
        await page.click('#mat-radio-5')

    if missing_teeth> 0:
        for i in range(missing_teeth):
            await page.click('#button-more-damage')
        if missing_teeth >1:
            await page.locator(".mat-checkbox-inner-container").click()

    if current_contract == True:
        await page.click('#mat-radio-6')
    else:
        await page.click('#mat-radio-7')


    await page.get_by_role("button", name="Weiter").click()
    await page.locator('[data-placeholder="PLZ"]').fill(data_json['plz'])
    await page.locator('[data-placeholder="Straße"]').fill(data_json['strasse'])
    await page.click('.mat-checkbox-inner-container')
    await page.locator('[data-placeholder="Hausnummer"]').fill(data_json['hausnr'])
    await page.locator('[data-placeholder="E-Mail-Adresse"]').fill(email)
    
    await page.locator('button:has-text("Weiter")').hover()
    await page.click('button:has-text("Weiter")')
    await page.locator('[data-placeholder="IBAN"]').fill(data_json['iban'])
    await page.click('.mat-checkbox-inner-container')
    await page.locator('button[type="submit"]').hover()
    await page.click('button[type="submit"]')


#------------------------------------------------------------------------
#
#
async def create_pdf(page ,name):
    async with page.expect_popup() as popup:
        await page.click('baf-link', modifiers=["Alt",])

    image_list =[]
    loader_page = await popup.value
    await loader_page.wait_for_url("blob:**")
    await loader_page.set_viewport_size({"width": 2480, "height": 3496})
    for p in range(print_pages):
        screenshot_path = name+"screenshot"+str(p)+".png"
        await loader_page.screenshot(path=screenshot_path, full_page=True)
        await loader_page.mouse.wheel(0, 3496)
        image = Image.open(r''+screenshot_path)
        im_con = image.convert('RGB')
        image_list.append(im_con)
    
    if name =="Extra":
        im_con.save('./media/pdfs/Mein_'+name+'_Angebot.pdf', save_all=True, append_images=image_list)
    else:
        im_con.save('./media/pdfs/Mein_Angebot.pdf', save_all=True, append_images=image_list)


    # delete screenshots after pdf is created
    for p in range(print_pages):
        screenshot_path = name+"screenshot"+str(p)+".png"
        os.remove(r''+screenshot_path)


