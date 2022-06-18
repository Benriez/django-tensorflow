from django.contrib import admin
from django.urls import path

from .models import Images


@admin.register(Images)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')


