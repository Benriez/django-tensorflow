import os
import json
import uuid 
import base64
import re

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.conf import settings

from playwright.async_api import async_playwright, expect
from PIL import Image

#
from .models import Customer



email = "admin@mail.com"
print_pages = 29
SITE_URL = getattr(settings, "SITE_URL", None)

class ScraperViewConsumer(AsyncWebsocketConsumer):
    group_name = "scraper"
    channel = ""
    url_offer = "https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=2&adm=00232070&app=makler"
    url_extra = "https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=1&app=makler&ADM=00232070"
    user_uuid = ""

    async def connect(self):
        self.user_uuid = await get_or_create_customer()
        self.channel = self.group_name+'_'+self.user_uuid
        await self.channel_layer.group_add(
            self.channel,
            self.channel_name
        )
        await self.accept()
        #create unique id
        await self.channel_layer.group_send(
            self.channel,
            {
                'type': 'get_unique_id',
                'data': {
                    'message': 'set_uuid',
                    'uuid': self.user_uuid,
                }
            }
        )
    
    async def disconnect(self, close_code):
        # Leave group
        print('disconnected')
    
    async def receive(self, text_data):
        # Receive data from WebSocket
        data_json = json.loads(text_data)
        if data_json['message'] == "check-uuid-exists":
            registered = await check_customer_exists(data_json['uuid'])
            if registered:
                await delete_customer(self.user_uuid)
                self.user_uuid = data_json['uuid']
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'checked_uuid',
                        'data': {
                            'message': 'checked-uuid',
                            'checked': True
                        }
                    }
                )
            else:
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'checked_uuid',
                        'data': {
                            'message': 'checked-uuid',
                            'checked': False,
                            'uuid': self.user_uuid
                        }
                    }
                )

        if data_json['message'] =="get-offer-price":
            await update_customer(self.user_uuid, data_json)
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
                    self.channel,
                    {
                        'type': 'get_offer_price',
                        'data': {
                            'message': 'Offer_Price',
                            'price': str_price,
                            'date': date
                        }
                    }
                )
        
        if data_json['message'] == 'offer-price-received':
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)
                
                #fill out external form
                small_price, medium_price, large_price, damage_text = await get_extra_price(page, data_json)           
                await browser.close()               
                # send result back to client
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'serve_extra_price',
                        'data': {
                            'message': 'serve_extra_price',
                            'small': small_price,
                            'medium': medium_price,
                            'large': large_price,
                            'damage_text': damage_text
                        }
                    }
                )  

        if data_json['message'] == 'extra-price-received':
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_offer)
                # other actions...
                
                #fill out external form
                await get_offer_pdf(page, data_json, self.user_uuid) 
                offer_link = await get_offer_link(self.user_uuid)
                await browser.close() 
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'serve_personal_offer',
                        'data': {
                            'message': 'Done',
                            'offer_link': offer_link
                        }
                    }
                )

    

        if data_json['message'] == "get_extra_pricelist":
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)
                
                #fill out external form
                small_price, medium_price, large_price, damage_text = await get_extra_price(page, data_json)           
                await browser.close()               
                # send result back to client
                await self.channel_layer.group_send(
                    self.channel,
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

        if data_json['message'] == "get_extra_offer_pdf":
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)

                await get_extra_pdf(page, data_json, self.user_uuid)
                #await page.pause()
                await browser.close() 
                
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'serve_price',
                        'data': {
                            'message': 'extra_done',
                        }
                    }
                )

        if data_json['message'] == "finish_orders":
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page_offer = await browser.new_page()
                page_extra = await browser.new_page()
                await page_offer.goto(self.url_offer)
                await page_extra.goto(self.url_extra)

                await finish_orders(page_offer, page_extra, data_json)
                
                
                await browser.close() 

                #send email to customer
                await send_email(self.user_uuid, data_json)

                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'congratulation',
                        'data': {
                            'message': 'Congrats',
                        }
                    }
                )

        elif data_json['message'] == "clear-data":
            pass
   

    #-----------------------------------------------------------------------------
    # 
    async def checked_uuid(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))
    
    async def get_unique_id(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def congratulation(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def get_offer_price(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_personal_offer(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_price(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_extra_price(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

@sync_to_async
def update_customer(user_id, data_json):
    customer = Customer.objects.get(client_id= user_id)
    customer.anrede = data_json["anrede"]
    customer.vorname = data_json["vorname"]
    customer.nachname = data_json["nachname"]
    customer.plz = data_json["plz"]
    customer.ort = data_json["ort"]
    customer.strasse = data_json["strasse"]
    customer.hausnr = data_json["hausnr"]
    customer.email = data_json["email"]
    customer.birthdate = data_json["birthdate"]
    # str to byte
    byteIban = bytes(data_json["iban"], encoding='utf8')
    # encode bytes
    encodedIban = base64.b64encode(byteIban)
    customer.iban = encodedIban
    customer.save()




class ExtraViewConsumer(AsyncWebsocketConsumer):
    group_name = "exscraper"
    channel = group_name
    url_extra = "https://ssl.barmenia.de/online-versichern/#/zahnversicherung/Beitrag?tarif=1&app=makler&ADM=00232070"
    user_uuid = ""

    async def connect(self):
 
        await self.channel_layer.group_add(
            self.channel,
            self.channel_name
        )
        await self.accept() 
        #create unique id
        await self.channel_layer.group_send(
            self.channel,
            {
                'type': 'get_unique_id',
                'data': {
                    'message': 'get_uuid'
                }
            }
        )

    async def disconnect(self, close_code):
        # Leave group
        print('disconnected')
        self.stop = True  # This will trigger the termination of loop # Maybe you also want to delete the thread
        raise StopConsumer

    async def receive(self, text_data):
        # Receive data from WebSocket
        data_json = json.loads(text_data)

        if data_json['message'] == "check-uuid-exists":
            registered = await check_customer_exists(data_json['uuid'])
            if registered:
                self.user_uuid = data_json['uuid']
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'checked_uuid',
                        'data': {
                            'message': 'checked-uuid',
                            'checked': True
                        }
                    }
                )
            else:
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'checked_uuid',
                        'data': {
                            'message': 'checked-uuid',
                            'checked': False
                        }
                    }
                )

                await self.disconnect()

         
        if data_json['message'] == 'get-extra-price':
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)
    
                #fill out external form
                small_price, medium_price, large_price, damage_text = await get_extra_price(page, data_json)           
                await browser.close()               
                # send result back to client
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'serve_extra_price',
                        'data': {
                            'message': 'serve_extra_price',
                            'small': small_price,
                            'medium': medium_price,
                            'large': large_price,
                            'damage_text': damage_text
                        }
                    }
                )  

        if data_json['message'] == 'get_extra_offer_pdf':
             async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url_extra)

                await get_extra_pdf(page, data_json, self.user_uuid)
                #await page.pause()
                await browser.close() 
                
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'serve_extra_pdf',
                        'data': {
                            'message': 'extra_done',
                        }
                    }
                )

        if data_json['message'] == "finish_orders":
            async with async_playwright() as playwright:
                chromium = playwright.webkit # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page_extra = await browser.new_page()
                await page_extra.goto(self.url_extra)

                await finish_extra_order(page_extra, data_json)  
                await browser.close() 

                #send email to customer
                await send_email(self.user_uuid, data_json, extra_only=True)

                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'congratulation',
                        'data': {
                            'message': 'Congrats',
                        }
                    }
                )
        


    #-----------------------------------------------------------------------------
    # 
    async def checked_uuid(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))
    async def get_unique_id(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_extra_price(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

    async def serve_extra_pdf(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))
    
    async def congratulation(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))

#----------------------------------------------------------------------------------
#
#
def gen_uuid():
    random_uuid= uuid.uuid4().hex[:16]
    return random_uuid

@sync_to_async
def get_or_create_customer(): 
    random_uuid= gen_uuid()
    try:
        client_id = Customer.objects.get(client_id= random_uuid)
        if client_id:
            gen_uuid()
    except:
        Customer.objects.create(client_id=random_uuid)

    return random_uuid

@sync_to_async
def check_customer_exists(str_uuid): 
    try:
        Customer.objects.get(client_id= str_uuid)
        return True
    except:
        return False

@sync_to_async
def delete_customer(user_uuid):
    try:
        customer = Customer.objects.get(client_id= user_uuid)
        customer.delete()
    except:
        print('something went wrong')


@sync_to_async
def send_email(user_uuid, data_json, extra_only=False):
    customer = Customer.objects.get(client_id = user_uuid)
    from_email = 'webmailer@zahnidee.de'
    extra_pdf = None
    offer_pdf = None

    if extra_only:
        extra_pdf = customer.extra_pdf.url
        mail_subject = 'Krankenzusatzversicherung'
        context = {
            "user": data_json["anrede"] + ' ' + data_json["vorname"] + ' ' +data_json["nachname"],
            "domain": SITE_URL,
            "offer_pdf": extra_pdf,
            "offer_only": True,
            # "uid":  urlsafe_base64_encode(force_bytes(user_pk)),
            # "token": account_activation_token.make_token(user),
            "paste_text": "Hello dear friend ...."
        }
    else:
        offer_pdf = customer.offer_pdf.url
        mail_subject = 'Angebot'
        context = {
            "user": data_json["anrede"] + ' ' + data_json["vorname"] + ' ' +data_json["nachname"],
            "domain": SITE_URL,
            "offer_pdf": offer_pdf,
            "extra_url": SITE_URL + '/extra/'+ str(user_uuid) + '/',
            # "uid":  urlsafe_base64_encode(force_bytes(user_pk)),
            # "token": account_activation_token.make_token(user),
            "paste_text": "Hello dear friend ...."
        }
        if data_json["extra_order"]==True:
            extra_pdf = customer.extra_pdf.url
            context["extra_pdf"]=extra_pdf
            context["extra_order"] = data_json["extra_order"]

    message = render_to_string('email/send_offer.html', context)   
    html_content = get_template("email/send_offer.html").render(context)
    msg = EmailMultiAlternatives(subject=mail_subject, body=message, from_email=from_email, to=['testreceiver@mail.com'])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    customer.success= True
    customer.save()




@sync_to_async
def get_offer_link(user_uuid):
    url = ''
    try:
        customer= Customer.objects.get(client_id = user_uuid)
        url=customer.offer_pdf.url
    except:
        pass

    return url

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



#-------------------------------------------------------------------
# STEPS
#
async def get_offer_pdf(page, data_json, user_uuid):
    await get_offer_step1(page, data_json)
    await get_offer_step2(page, data_json)
    await create_pdf(page, user_uuid, name='personal')



async def get_extra_pdf(page, data_json, user_uuid):
    await get_extra_step1(page, data_json)
    await get_extra_step2(page, data_json)
    await create_pdf(page, user_uuid , name='Extra')
    #await page.pause()


async def finish_orders(page_offer, page_extra, data_json):
    # offer and extra?
    # get offer
    await get_offer_step1(page_offer, data_json)
    await get_offer_step2(page_offer, data_json)
    # get offer rest

    # get extra
    if data_json["extra_order"]:
        await get_extra_step1(page_extra, data_json)
        await get_extra_step2(page_extra, data_json)
    #get extra rest


async def finish_extra_order(page_extra, data_json):
    await get_extra_step1(page_extra, data_json)
    await get_extra_step2(page_extra, data_json)

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

@sync_to_async
def upload_pdf(user_uuid, im_con, name, image_list):
    customer = Customer.objects.get(client_id = user_uuid)
    filename = 'Mein_Angebot.pdf'
    extra_filename = 'Mein_'+name+'_Angebot.pdf'
    media_path = './media/pdfs/'

    if name =="Extra":
        im_con.save(media_path + extra_filename, save_all=True, append_images=image_list, optimize=True, quality=80)
        local_file = open(media_path+extra_filename)
        extra_pdf = File(local_file)
        customer.extra_pdf.save(extra_filename, File(open(str(extra_pdf),'rb')))
        local_file.close()
    else:
        im_con.save(media_path + filename, save_all=True, append_images=image_list,optimize=True,quality=80)
        local_file = open(media_path + filename)
        offer_pdf = File(local_file)
        customer.offer_pdf.save(filename, File(open(str(offer_pdf),'rb')))
        local_file.close()




async def create_pdf(page, user_uuid ,name):
    async with page.expect_popup() as popup:
        await page.click('baf-link', modifiers=["Alt",])
    image_list =[]
    # await page.pause()
    pdf_page = await popup.value
    await pdf_page.wait_for_load_state()
    await pdf_page.wait_for_url(r"blob:**")

    #await pdf_page.wait_for_selector("embed")

    await pdf_page.set_viewport_size({"width": 2480, "height": 3496})
    for p in range(print_pages):
        screenshot_path = user_uuid + '_' +name+"screenshot"+str(p)+".jpg"

        await pdf_page.screenshot(path=screenshot_path, full_page=True)
        await pdf_page.mouse.wheel(0, 3496)
        image = Image.open(r''+screenshot_path)
        im_con = image.convert('RGB')
        image_list.append(im_con)
    
    await upload_pdf(user_uuid, im_con, name, image_list)
    # delete screenshots after pdf is created
    for p in range(print_pages):
        screenshot_path = user_uuid + '_' +name+"screenshot"+str(p)+".jpg"
        os.remove(r''+screenshot_path)


