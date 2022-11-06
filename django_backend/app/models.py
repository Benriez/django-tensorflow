from django.db import models
from django.core.validators import deconstructible
from storages.backends.s3boto3 import S3Boto3Storage

FOLDER_PDF   = 'users/'
FOLDER_STANDARD_PDF = 'standards/'


#-------------------------------------------------------------------
def get_upload_path(instance, filename):
    storage = get_pdf_storage()
    return storage.get_upload_path(instance, filename)

def get_standard_upload_path(instance, filename):
    storage = get_standard_pdf_storage()
    return storage.get_upload_path(instance, filename)




#-------------------------------------------------------------------
@deconstructible
class PDFStorage(S3Boto3Storage):
    location = '{}'.format(FOLDER_PDF)

    print('---> PDFstorage location=[' + location + "]")

    def get_upload_path(self, instance, filename):
        upload_path = str(instance.id) + "/"+ filename
        return upload_path


@deconstructible
class StandardPDFStorage(S3Boto3Storage):
    location = '{}'.format(FOLDER_STANDARD_PDF)

    print('---> PDFstorage location=[' + location + "]")

    def get_upload_path(self, instance, filename):
        return filename


#-----------------------------------------------------------------------------------------------------------------
pdf_storage = PDFStorage()
standard_pdf_storage = StandardPDFStorage()


def get_pdf_storage():
    return pdf_storage

def get_standard_pdf_storage():
    return standard_pdf_storage



#-----------------------------------------------------------------------------------------------------------------
class Customer(models.Model):
    client_id   = models.CharField(max_length=30, null=True, unique=True)
    offer_pdf   = models.FileField(storage=get_pdf_storage(), upload_to=get_upload_path, blank=True, null=True) #upload_to='documents/'
    extra_pdf   = models.FileField(storage=get_pdf_storage(), upload_to=get_upload_path,blank=True, null=True)
    success     = models.BooleanField(default=False)
    email       = models.EmailField(('email address'), blank=True)
    date        = models.DateTimeField("Erstellt am", auto_now=True) 

    anrede      = models.CharField(max_length=10, null=True)
    vorname     = models.CharField(max_length=30, null=True)
    nachname    = models.CharField(max_length=30, null=True)
    plz         = models.CharField(max_length=8, null=True)
    ort         = models.CharField(max_length=30, null=True)
    strasse     = models.CharField(max_length=30, null=True)
    hausnr      = models.CharField(max_length=30, null=True)
    iban        = models.BinaryField(default=b'\x08')
    birthdate   = models.CharField(max_length=50, null=True)
    class Meta:
        app_label = 'Customer'

    def __str__(self):
        return self.client_id


class StandardPDF(models.Model):
    name    = models.CharField(max_length=30)
    pdf     = models.FileField(storage=get_standard_pdf_storage(), upload_to=get_standard_upload_path, blank=True, null=True)

    class Meta:
        app_label = 'StandardPDF'

    def __str__(self):
        return self.name
