# Generated by Django 4.0.5 on 2022-11-04 20:10

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_customer_extra_pdf_remove_customer_offer_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='extra_pdf',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
        migrations.AddField(
            model_name='customer',
            name='offer_pdf',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
    ]
