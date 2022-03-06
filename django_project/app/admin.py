from django.contrib import admin
from django.urls import path

from .models import Images


@admin.register(Images)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'kontakt')

    def kontakt(self, obj):
        try:
            contact = obj.anrede + " " + obj.vorname_ansprechpartner + " " + obj.nachname_ansprechpartner        
        except:
            contact = obj.name
            
        return contact 