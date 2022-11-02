from django.contrib import admin
from django.urls import path

from .models import Customer


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'offer_pdf', 'extra_pdf', 'success')


