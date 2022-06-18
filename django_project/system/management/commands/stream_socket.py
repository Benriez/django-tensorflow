from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.management import BaseCommand
import psutil


class Command(BaseCommand):
    help = 'Command to start stream socket data if any socket open'

    def handle(self, *args, **options):
        group_name = settings.STREAM_SOCKET_GROUP_NAME
        channel_layer = get_channel_layer()
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'system_load',
                'data': {
                    'cpu_percent': cpu_percent,
                    'ram_percent': ram_percent
                }
            }
        )