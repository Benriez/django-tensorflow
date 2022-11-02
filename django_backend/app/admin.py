from django.contrib import admin
from django.urls import path

from .models import Customer, StandardPDF


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'offer_pdf', 'extra_pdf', 'success', 'date')


@admin.register(StandardPDF)
class StandardPDFModelAdmin(admin.ModelAdmin):
    pass

