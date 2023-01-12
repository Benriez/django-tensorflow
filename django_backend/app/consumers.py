import os
import json
import uuid 
import base64
import datetime

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.conf import settings
# import tensorflow as tf

from .models import Customer


SITE_URL = getattr(settings, "SITE_URL", None)
DEBUG = getattr(settings, "DEBUG", bool)
SKIP_EMAIL = getattr(settings, "SKIP_EMAIL", bool)
ARMED = getattr(settings, "ARMED", bool)
date_today = datetime.datetime.now().strftime ("%d.%m.%Y")


if not os.path.exists('./media/pdfs/'):
    os.makedirs('./media/pdfs/')



class ScraperViewConsumer(AsyncWebsocketConsumer):
    group_name = "scraper"
    channel = ""
    user_uuid = ""
    customer_age = -1

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
        pass
   

    #-----------------------------------------------------------------------------
    # 
    async def checked_uuid(self, event):
        # Receive data from group
        await self.send(text_data=json.dumps(event['data']))
    
    async def get_unique_id(self, event):
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

    return customer.birthdate



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
    from_email = ''
    mail_subject = 'Zahnversicherung'
    context = {
        "user": 'USER',
        "domain": SITE_URL,
    }
    message = render_to_string('email/send_offer.html', context)   
    html_content = get_template("email/send_offer.html").render(context)
    msg = EmailMultiAlternatives(subject=mail_subject, body=message, from_email=from_email, to=[data_json["email"]])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    customer.success= True
    customer.save()




