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

from PyPDF2 import PdfFileWriter, PdfFileReader,PdfMerger
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
#
from .models import Customer, StandardPDF
import os
import datetime


email = "mco@mv24.de"
print_pages = 29
SITE_URL = getattr(settings, "SITE_URL", None)
DEBUG = getattr(settings, "DEBUG", bool)
SKIP_EMAIL = getattr(settings, "SKIP_EMAIL", None)
ARMED = getattr(settings, "ARMED", False)
date_today = datetime.datetime.now().strftime ("%d.%m.%Y")
playwright_tries = 3

if not os.path.exists('./media/pdfs/'):
    os.makedirs('./media/pdfs/')

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
        if DEBUG:
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
                #try:
                date, str_price = await get_offer_price(page, data_json)
                #except:
                    # await self.channel_layer.group_send(
                    #     self.channel,
                    #     {
                    #         'type': 'timeout_exception',
                    #         'data': {
                    #             'message': 'Please reload the page'
                    #         }
                    #     }
                    # )
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
                chromium = playwright.chromium # or "firefox" or "webkit".
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
                extra_link = await get_extra_link(self.user_uuid)
                await browser.close() 
                await self.channel_layer.group_send(
                    self.channel,
                    {
                        'type': 'serve_personal_offer',
                        'data': {
                            'message': 'Done',
                            'offer_link': offer_link,
                            'extra_link': extra_link
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
                chromium = playwright.chromium # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page_offer = await browser.new_page()
                page_extra = await browser.new_page()
                await page_offer.goto(self.url_offer)
                await page_extra.goto(self.url_extra)

                await finish_orders(page_offer, page_extra, data_json)
                
                
                await browser.close() 

                #send email to customer
          
                print('send email')
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
        if DEBUG:
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
                chromium = playwright.chromium # or "firefox" or "webkit".
                browser = await chromium.launch(headless=True)
                page_extra = await browser.new_page()
                await page_extra.goto(self.url_extra)

                await finish_extra_order(page_extra, data_json)  
                await browser.close() 

                #send email to customer
                if SKIP_EMAIL:
                    pass
                else: 
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
        if DEBUG:
            print('something went wrong')


@sync_to_async
def send_email(user_uuid, data_json, extra_only=False):
    customer = Customer.objects.get(client_id = user_uuid)
    from_email = 'mco@mv24.de'
    extra_pdf = None
    offer_pdf = None

    if extra_only:
        extra_pdf = customer.extra_pdf.url
        mail_subject = 'Zahnversicherung'
        context = {
            "user": data_json["anrede"] + ' ' + data_json["vorname"] + ' ' +data_json["nachname"],
            "domain": SITE_URL,
            "offer_pdf": extra_pdf,
            "offer_only": True
        }
    else:
        offer_pdf = customer.offer_pdf.url
        mail_subject = 'Zahnversicherung'
        context = {
            "user": data_json["anrede"] + ' ' + data_json["vorname"] + ' ' +data_json["nachname"],
            "domain": SITE_URL,
            "offer_pdf": offer_pdf,
            "extra_url": 'https://'+ SITE_URL + '/extra/'+ str(user_uuid) + '/',
        }
        if data_json["extra_order"]==True:
            extra_pdf = customer.extra_pdf.url
            context["extra_pdf"]=extra_pdf
            context["extra_order"] = data_json["extra_order"]

    message = render_to_string('email/send_offer.html', context)   
    html_content = get_template("email/send_offer.html").render(context)
    msg = EmailMultiAlternatives(subject=mail_subject, body=message, from_email=from_email, to=[data_json["email"]])
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

@sync_to_async
def get_extra_link(user_uuid):
    url = ''
    try:
        customer= Customer.objects.get(client_id = user_uuid)
        url=customer.extra_pdf.url
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
    await create_pdf(page, user_uuid, data_json, name='personal')


async def get_extra_pdf(page, data_json, user_uuid):
    await create_pdf(page, user_uuid , data_json, name='Extra')


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
    await page.locator('[data-placeholder="Versicherungsbeginn"]').fill(data_json['versicherungsbeginn'])
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

    await page.locator(".mat-checkbox-inner-container").first.click()
    await page.locator("#mat-checkbox-5 > .mat-checkbox-layout > .mat-checkbox-inner-container").click()
    await page.get_by_role("button", name="Weiter").click()
    
    if ARMED == "True":
        await page.get_by_role("button", name="Beitragspflichtig abschließen").click()
    

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

    await page.locator(".mat-checkbox-inner-container").first.click()
    await page.locator("#mat-checkbox-5 > .mat-checkbox-layout > .mat-checkbox-inner-container").click()
    await page.get_by_role("button", name="Weiter").click()

    if ARMED == "True":
        await page.get_by_role("button", name="Beitragspflichtig abschließen").click()


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


@sync_to_async
def create_pdf(page, user_uuid ,data_json, name):
    if DEBUG:
        print('----create pdf----')

    customer = Customer.objects.get(client_id=user_uuid)
    head_1 = build_head_1(user_uuid, customer, data_json)
    head_2 = build_head_2(user_uuid, customer, data_json, name)
    third_base = StandardPDF.objects.get(name="third_base").pdf
    
    #second base
    if name=="Extra":
        head_4 = build_head_4(user_uuid, customer, data_json)
        head_5 = build_head_5(user_uuid, customer, data_json)
        head_6 = StandardPDF.objects.get(name="head_6_extra").pdf


        second_base_1 = build_extra_second_base_1(user_uuid, customer, data_json)
        second_base_2 = build_extra_second_base_2(user_uuid, customer, data_json)
        second_base_3 = build_extra_second_base_3(user_uuid, customer, data_json)
        second_base_4 = build_extra_second_base_4(user_uuid, customer, data_json)
    else:
        head_3 = build_head_3(user_uuid, customer, data_json)
        head_6 = StandardPDF.objects.get(name="head_6").pdf
        second_base_1 = StandardPDF.objects.get(name="second_base_1").pdf
        second_base_2 = StandardPDF.objects.get(name="second_base_2").pdf
        second_base_3 = StandardPDF.objects.get(name="second_base_3").pdf
        second_base_4 = StandardPDF.objects.get(name="second_base_4").pdf


    if name=="Extra":
        pdfs = [
            head_1, head_2, head_5, head_4, head_6,
            second_base_1, second_base_2, second_base_3, second_base_4,
            third_base
        ]
    else:
        pdfs = [
            head_1, head_2, head_3, head_6,
            second_base_1, second_base_2, second_base_3, second_base_4,
            third_base
        ]

    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    if name == "Extra":
        pdfname = "_extra.pdf"
    else:
        pdfname = "_offer.pdf"
    pdf_path = user_uuid + pdfname

    merger.write("./media/pdfs/"+ pdf_path)
    merger.close()

    local_file = open("./media/pdfs/"+pdf_path)
    _pdf = File(local_file)
    
    if name == "Extra":
        filename="Extra_"+pdf_path
        customer.extra_pdf.save(filename, File(open(str(_pdf),'rb')))
    else:
        filename="Offer_"+pdf_path
        customer.offer_pdf.save(filename, File(open(str(_pdf),'rb')))

    local_file.close()

    # remove offer or extra pdf loacally
    os.remove(r'./media/pdfs/'+pdf_path)

    #remove custom head objs from s3 storage after merge completed
    customer.head_1.delete(save=False)
    customer.head_1 = None
    customer.head_2.delete(save=False)
    customer.head_2 = None
    customer.head_3.delete(save=False)
    customer.head_3 = None
    customer.head_4.delete(save=False)
    customer.head_4 = None
    customer.head_5.delete(save=False)
    customer.head_5 = None
    customer.save()


    if name == "Extra":
        customer.second_base_1.delete(save=False)
        customer.second_base_1 = None
        customer.second_base_2.delete(save=False)
        customer.second_base_2 = None
        customer.second_base_3.delete(save=False)
        customer.second_base_3 = None
        customer.second_base_4.delete(save=False)
        customer.second_base_4 = None
        customer.second_base_5.delete(save=False)
        customer.second_base_5 = None
        customer.save()
        if DEBUG:
            print('Done Extra')
    else:
        if DEBUG:
            print('Done Offer')
        

def build_head_1(user_uuid, customer, data_json):
    if DEBUG:
        print('----build head 1') 
    
    head_1 = StandardPDF.objects.get(name="head_1")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica', 38)
    can.drawString(321, 2764, data_json["anrede"])
    can.drawString(321, 2718, data_json["vorname"] + ' ' + data_json["nachname"])
    can.drawString(321, 2672, data_json["strasse"] + ' ' + data_json["hausnr"])
    can.drawString(321, 2626, data_json["plz"] +' '+ data_json["ort"])
    can.drawString(1574, 2237, date_today)

    can.setFont('Helvetica', 42)
    can.drawString(490, 2056, data_json["anrede"] + ' ' + data_json["nachname"] + ',')

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    head_obj = head_creator(packet, head_1, user_uuid, customer, iterator=1)
    return head_obj
    


def build_head_2(user_uuid, customer, data_json, name):
    if DEBUG:
        print('----build head 2') 
    head_2 = StandardPDF.objects.get(name="head_2")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica', 42)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(757, 2437, data_json["versicherungsbeginn"][:-1])
    can.drawString(328, 2231, data_json["vorname"] +' '+data_json["nachname"])
    can.drawString(1302, 2231, data_json["birthdate"])
    can.setFillColorRGB(254,255,255)
    can.drawString(328, 2068, data_json["vorname"] +' '+data_json["nachname"])
    
    can.setFillColorRGB(0.34765625,0.34765625,0.34765625)
    if name =="Extra":
        can.drawString(328, 1913, data_json["tarif"])
        can.drawString(1512, 1913, data_json["shortdesc_tarif"])
        can.drawString(2023, 1913, data_json["str_extra_price"])
        can.drawString(2023, 1790, data_json["str_extra_price"])
    else:
        can.drawString(328, 1913, "ZahnReinigungsFlat by Zahnidee")
        can.drawString(1512, 1913, "ZAHNV")
        can.drawString(2023, 1913, data_json["str_price"])
        can.drawString(2023, 1790, data_json["str_price"])

    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    head_obj = head_creator(packet, head_2, user_uuid, customer, iterator=2)
    return head_obj


def build_head_3(user_uuid, customer, data_json):
    if DEBUG:
        print('----build head 3') 
    head_3 = StandardPDF.objects.get(name="head_3")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica', 42)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(684, 2491, data_json["vorname"] +' '+data_json["nachname"])

    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    head_obj = head_creator(packet, head_3, user_uuid, customer, iterator=3)
    return head_obj


def build_head_4(user_uuid, customer, data_json):
    if DEBUG:
        print('----build head 4') 
    head_4 = StandardPDF.objects.get(name="head_4")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica', 42)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(686, 2491, data_json["vorname"] +' '+data_json["nachname"])
    
    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica', 34)
    if data_json["shortdesc_tarif"] =="ZAHN80":
        can.drawString(325, 2196, "80% ")
    elif data_json["shortdesc_tarif"] =="ZAHN90":
        can.drawString(325, 2196, "90% ")
    elif data_json["shortdesc_tarif"] =="ZAHN100":
        can.setFont('Helvetica', 33)
        can.drawString(320, 2196, "100% ")

    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    head_obj = head_creator(packet, head_4, user_uuid, customer, iterator=4)
    return head_obj


def build_head_5(user_uuid, customer, data_json):
    if DEBUG:
        print('----build head 5') 
    head_5 = StandardPDF.objects.get(name="head_5")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica', 42)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(273, 2898, data_json["vorname"] +' '+data_json["nachname"])
    can.setFont('Helvetica', 46)
    can.setFillColorRGB(0,0,0)

    if data_json["extra_behandlung"] == True:
        can.drawString(1670, 2710, "X")
    else:
        can.drawString(1745, 2710, "X")

    if data_json["missing_teeth"] > 0:
        can.drawString(1670, 2613, "X")
        can.setFont('Helvetica', 38)
        can.drawString(335, 2565, str(data_json["missing_teeth"]))
    else:
        can.setFont('Helvetica', 38)
        can.drawString(1745, 2613, "X")
        can.drawString(335, 2565, "0")
        
    if data_json["current_contract"] == True:
        can.drawString(1670, 2513, "X")
    else:
        can.drawString(1745, 2513, "X")
        
    can.save()
    #move to the beginning of the StringIO buffer
    packet.seek(0)
    head_obj = head_creator(packet, head_5, user_uuid, customer, iterator=5)
    return head_obj


def build_extra_second_base_1(user_uuid, customer, data_json):
    if DEBUG:
        print('----build extra second base 1') 
    secondbase_1 = StandardPDF.objects.get(name="second_base_1_extra")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica-Bold', 38)
    can.drawString(398, 2709, data_json["tarif"])
    can.setFont('Helvetica-Bold', 32)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(1068, 2300, data_json["tarif"])
    can.drawString(550, 1987, data_json["tarif"])
    can.drawString(660, 1877, data_json["tarif"])
    can.drawString(1219, 1877, data_json["tarif"])
    can.drawString(1219, 1577, data_json["tarif"])
    can.setFillColorRGB(0.34765625,0.34765625,0.34765625)
    if data_json["tarif"] == "Mehr Zahn 80":
        can.drawString(1150, 1196, "80")
    elif data_json["tarif"] == "Mehr Zahn 90":
        can.drawString(1150, 1196, "90")
    elif data_json["tarif"] == "Mehr Zahn 100":
        can.drawString(1150, 1196, "100")
    

    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(1152, 750, data_json["tarif"])
    can.drawString(931, 611, data_json["tarif"])


    can.save()
    packet.seek(0)
    second_base_obj = base_creator(packet, secondbase_1, user_uuid, customer, iterator=1)
    if DEBUG:
        print('finish second base 1')
    return second_base_obj
    

def build_extra_second_base_2(user_uuid, customer, data_json):
    if DEBUG:
        print('----build extra second base 2') 
    secondbase = StandardPDF.objects.get(name="second_base_2_extra")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica-Bold', 32)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(1006, 3026, data_json["tarif"])
    can.setFillColorRGB(0.34765625,0.34765625,0.34765625)

    if data_json["tarif"] == "Mehr Zahn 80":
        can.drawString(761, 2477, "80%")
    elif data_json["tarif"] == "Mehr Zahn 90":
        can.drawString(761, 2477, "90%")
    elif data_json["tarif"] == "Mehr Zahn 100":
        can.drawString(761, 2477, "100%")

    can.save()
    packet.seek(0)
    second_base_obj = base_creator(packet, secondbase, user_uuid, customer, iterator=2)
    return second_base_obj


def build_extra_second_base_3(user_uuid, customer, data_json):
    if DEBUG:
        print('----build extra second base 3') 
    secondbase = StandardPDF.objects.get(name="second_base_3_extra")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica', 32)
    can.drawString(1153, 728, data_json["tarif"])
    can.drawString(376, 682, data_json["tarif"])
    can.drawString(1064, 682, data_json["tarif"])
    can.drawString(931, 590, data_json["tarif"])


    can.save()
    packet.seek(0)
    second_base_obj = base_creator(packet, secondbase, user_uuid, customer, iterator=3)
    return second_base_obj


def build_extra_second_base_4(user_uuid, customer, data_json):
    if DEBUG:
        print('----build extra second base 4') 
    secondbase = StandardPDF.objects.get(name="second_base_4_extra")
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setPageSize((2381, 3368))
    can.setFont('Helvetica-Bold', 32)
    can.setFillColorRGB(0,0.6171875,0.875)
    can.drawString(1126, 3025, data_json["tarif"])
    can.drawString(1024, 2870, data_json["tarif"])
    can.drawString(1645, 2708, data_json["tarif"])

    can.save()
    packet.seek(0)
    second_base_obj = base_creator(packet, secondbase, user_uuid, customer, iterator=4)
    return second_base_obj



def base_creator(packet, obj, user_uuid, customer, iterator):
    if DEBUG:
        print('baseCReator')

    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(obj.pdf.open())
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # finally, write "output" to a real file
    base_path = "Base"+str(iterator)+ ".pdf"
    if not os.path.exists('./media/pdfs/'+user_uuid+'/'):
        os.makedirs('./media/pdfs/'+user_uuid+'/')

    outputStream = open("./media/pdfs/"+ user_uuid +'/'+base_path, "wb")
    output.write(outputStream)
    outputStream.close()
    
    local_file = open("./media/pdfs/"+ user_uuid +'/'+base_path)
    base_pdf = File(local_file)
    filename="Base_"+str(iterator)+".pdf"

    if iterator == 1:
        customer.second_base_1.save(filename, File(open(str(base_pdf),'rb')))
    elif iterator == 2:
        customer.second_base_2.save(filename, File(open(str(base_pdf),'rb')))
    elif iterator == 3:
        customer.second_base_3.save(filename, File(open(str(base_pdf),'rb')))
    elif iterator == 4:
        customer.second_base_4.save(filename, File(open(str(base_pdf),'rb')))


    
    local_file.close()
    os.remove(r'./media/pdfs/'+user_uuid +'/'+ base_path)

    if DEBUG:
        print('Done Base: ['+ str(iterator)  +']')
    
    if iterator == 1:
        return customer.second_base_1
    elif iterator == 2:
        return customer.second_base_2
    elif iterator == 3:
        return customer.second_base_3
    elif iterator == 4:
        return customer.second_base_4
    elif iterator == 5:
        return customer.second_base_5



def head_creator(packet, obj, user_uuid, customer, iterator):
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(obj.pdf.open())
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # finally, write "output" to a real file
    head_path = "head"+str(iterator)+ ".pdf"
    if not os.path.exists('./media/pdfs/'+user_uuid+'/'):
        os.makedirs('./media/pdfs/'+user_uuid+'/')

    outputStream = open("./media/pdfs/"+ user_uuid +'/'+head_path, "wb")
    output.write(outputStream)
    outputStream.close()
    
    local_file = open("./media/pdfs/"+ user_uuid +'/'+head_path)
    head_pdf = File(local_file)
    filename="Head_"+str(iterator)+".pdf"

    if iterator == 1:
        customer.head_1.save(filename, File(open(str(head_pdf),'rb')))
    elif iterator == 2:
        customer.head_2.save(filename, File(open(str(head_pdf),'rb')))
    elif iterator == 3:
        customer.head_3.save(filename, File(open(str(head_pdf),'rb')))
    elif iterator == 4:
        customer.head_4.save(filename, File(open(str(head_pdf),'rb')))
    elif iterator == 5:
        customer.head_5.save(filename, File(open(str(head_pdf),'rb')))

    
    local_file.close()
    os.remove(r'./media/pdfs/'+user_uuid +'/'+ head_path)

    
    if iterator == 1:
        return customer.head_1
    elif iterator == 2:
        return customer.head_2
    elif iterator == 3:
        return customer.head_3
    elif iterator == 4:
        return customer.head_4
    elif iterator == 5:
        return customer.head_5

    if DEBUG:
        print('Done Head: ['+ str(iterator)  +']')


# async def create_pdf(page, user_uuid ,name):
#     async with page.expect_popup() as popup:
#         await page.click('baf-link', modifiers=["Alt",])
#     image_list =[]
#     pdf_page = await popup.value

#     #await pdf_page.wait_for_url(r"blob:**")
#     print('try wait for selector "embed"...')
#     try:
#         await pdf_page.wait_for_selector("embed", timeout = 30000)
#     except:
#         print('cant wait for selector [embed] at url: ', pdf_page.url)
#         print('try wait for url [blob]')
#         await pdf_page.wait_for_url(r"blob:**")
        

#     await pdf_page.set_viewport_size({"width": 2480, "height": 3496})
#     for p in range(print_pages):
#         screenshot_path = user_uuid + '_' +name+"screenshot"+str(p)+".jpg"

#         await pdf_page.screenshot(path=screenshot_path, full_page=True)
#         await pdf_page.mouse.wheel(0, 3496)
#         image = Image.open(r''+screenshot_path)
#         im_con = image.convert('RGB')
#         image_list.append(im_con)
    
#     await upload_pdf(user_uuid, im_con, name, image_list)
#     # delete screenshots after pdf is created
#     for p in range(print_pages):
#         screenshot_path = user_uuid + '_' +name+"screenshot"+str(p)+".jpg"
#         os.remove(r''+screenshot_path)


