from django.utils.html import mark_safe
from django.db import models
from django.utils.timezone import now



class Customer(models.Model):
    client_id   = models.CharField(max_length=30)
    offer_pdf   = models.FileField(blank=True, null=True)
    extra_pdf   = models.FileField(blank=True, null=True)
    success     = models.BooleanField(default=False)
    email       = models.EmailField(('email address'), blank=True)
    date        = models.DateTimeField("Erstellt am", auto_now=True) 

    def __str__(self):
        return self.client_id


class StandardPDF(models.Model):
    name    = models.CharField(max_length=30)
    pdf     = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.name
