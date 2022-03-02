from djmoney.models.fields import MoneyField
from django.db import models
from django.utils.timezone import now


class Customer(models.Model):
    name                            = models.CharField("Firmenname", max_length=128, blank=True, null=True)
    website                         = models.CharField("Firmenwebseite", max_length=50, blank=True, null=True)
    anrede                          = models.CharField("Anrede", max_length=20, blank=True, null=True)
    vorname_ansprechpartner         = models.CharField("Vorname Ansprechpartner", max_length=50, blank=True, null=True)
    nachname_ansprechpartner        = models.CharField("Nachname Ansprechpartner", max_length=50, blank=True, null=True)
    email_ansprechpartner           = models.CharField("Email Ansprechpartner", max_length=50, blank=True, null=True)
    phone_ansprechpartner           = models.CharField("Telefon Ansprechpartner", max_length=20, blank=True)
    phone                           = models.CharField("Telefon", max_length=20, blank=True)
    street                          = models.CharField("Straße", max_length=100, blank=True)
    haus_nr                         = models.CharField("Haus-Nr.", max_length=10, blank=True)
    zip_code                        = models.CharField("PLZ", max_length=20, blank=True, null=True)
    ort                             = models.CharField("Ort", max_length=10, blank=True)
    billing_address                 = models.CharField('Rechnungsadresse', max_length=300, blank=True)
    comment                         = models.TextField("Kommentar", max_length=1000, blank=True)


    class Meta:
        verbose_name = 'Kunde'
        verbose_name_plural = 'Kunden'

    def __str__(self):
        return self.name
    

class Product(models.Model):
    product_name    = models.CharField("Produkt Name", max_length=32)
    preis           = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency="EUR")
    comment         = models.TextField("Kommentar", max_length=1000, blank=True)

    
    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkte'

    def __str__(self):
        return self.product_name    



class Order(models.Model):
    auftragstyp     = models.CharField("Auftragstyp", max_length=128, blank=True, null=True)
    menge           = models.IntegerField(default=0)
    produkt         = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    kunde           = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE)
    comment         = models.TextField("Kommentar", max_length=1000, blank=True)
    erstellt        = models.DateTimeField(default=now, blank=True)
    
    
    class Meta:
        verbose_name = 'Bestellung'
        verbose_name_plural = 'Bestellungen'
    
    def __str__(self):
        try: 
            name = '#' +str(self.id) + ', ' + self.kunde.name
        except:
            name = '#' +str(self.id)
        return name
    


class Termine(models.Model):
    termintyp       = models.CharField("Termintyp", max_length=128, blank=True, null=True)
    menge           = models.IntegerField(default=0)
    produkt         = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    kunde           = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE)
    comment         = models.TextField("Kommentar", max_length=1000, blank=True)
    erstellt        = models.DateTimeField(default=now, blank=True)
    datum           = models.DateTimeField("Termindatum",blank=True, null=True)
    
    class Meta:
        verbose_name = 'Termin'
        verbose_name_plural = 'Termine'
    
    def __str__(self):
        try: 
            name = '#' +str(self.id) + ', ' + self.kunde.name
        except:
            name = '#' +str(self.id)
        return name
    


class Signale(models.Model):
    auftragstyp     = models.CharField("Signaltyp", max_length=128, blank=True, null=True)
    menge           = models.IntegerField(default=0)
    produkt         = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    kunde           = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE)
    comment         = models.TextField("Kommentar", max_length=1000, blank=True)
    erstellt        = models.DateTimeField(default=now, blank=True)
    
    
    class Meta:
        verbose_name = 'Kundensignal'
        verbose_name_plural = 'Kundensignale'
    
    def __str__(self):
        try: 
            name = '#' +str(self.id) + ', ' + self.kunde.name
        except:
            name = '#' +str(self.id)
        return name
    

class CRM(models.Model):
    class Meta:
        verbose_name = 'CRM-Integration'
        verbose_name_plural = 'CRM-Integration'
        app_label = 'app' 


class Kommunikationstool(models.Model):
    class Meta:
        verbose_name = 'Kommunikationstool'
        verbose_name_plural = 'Kommunikationstool'
        app_label = 'app' 


class Warenwirtschaftssystem(models.Model):
    class Meta:
        verbose_name = 'Warenwirtschaftssystem'
        verbose_name_plural = 'Warenwirtschaftssystem'
        app_label = 'app' 