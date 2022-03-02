from django.contrib import admin
from django.urls import path

from .models import Customer, Product, Order, Termine, Signale, CRM, Kommunikationstool, Warenwirtschaftssystem

from .views import CRMView, KommunikationstoolView, WarenwirtschaftssystemView


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'kontakt')

    def kontakt(self, obj):
        try:
            contact = obj.anrede + " " + obj.vorname_ansprechpartner + " " + obj.nachname_ansprechpartner        
        except:
            contact = obj.name
            
        return contact


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'preis', 'comment',)


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'kunde', 'erstellt',)
    pass


@admin.register(Termine)
class TerminModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'kunde', 'datum', 'comment',)


@admin.register(Signale)
class SignalModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'kunde', 'erstellt',)    


@admin.register(CRM)
class CRMModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
                CRM._meta.app_label, CRM._meta.model_name)
        return [
            path('', CRMView.as_view(), name=view_name)
        ] 

@admin.register(Kommunikationstool)
class KommunikationstoolModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
                Kommunikationstool._meta.app_label, Kommunikationstool._meta.model_name)
        return [
            path('', KommunikationstoolView.as_view(), name=view_name) 
        ] 


@admin.register(Warenwirtschaftssystem)
class WarenwirtschaftssystemModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
                Warenwirtschaftssystem._meta.app_label, Warenwirtschaftssystem._meta.model_name)
        return [
            path('', WarenwirtschaftssystemView.as_view(), name=view_name)
        ] 