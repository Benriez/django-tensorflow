from djmoney.models.fields import MoneyField
from django.db import models
from django.utils.timezone import now


class Images(models.Model):
    name                            = models.CharField("Filename", max_length=128, blank=True, null=True)
    website                         = models.CharField("Website", max_length=50, blank=True, null=True)
    comment                         = models.TextField("Comment", max_length=1000, blank=True)


    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def __str__(self):
        return self.name
    

