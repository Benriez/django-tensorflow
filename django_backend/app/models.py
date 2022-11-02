from django.utils.html import mark_safe
from django.db import models
from django.utils.timezone import now



class Customer(models.Model):
    client_id   = models.CharField(max_length=30)
    offer_pdf   = models.FileField(blank=True, null=True)
    extra_pdf   = models.FileField(blank=True, null=True)
    success     = models.BooleanField(default=False)




class Images(models.Model):
    name        = models.CharField("Filename", max_length=128, blank=True, null=True)
    website     = models.CharField("Website", max_length=50, blank=True, null=True)
    comment     = models.TextField("Comment", max_length=1000, blank=True)
    file        = models.ImageField("Datei", blank=True, null=True, upload_to="img")
    displayed   = models.BooleanField(default=False)
    seen        = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def __str__(self):
        return self.name
    
    # def image_tag(self):
    #     return mark_safe('<img src="/directory/%s" width="150" height="150" />' % (self.image))

    # image_tag.short_description = 'Image'
    

