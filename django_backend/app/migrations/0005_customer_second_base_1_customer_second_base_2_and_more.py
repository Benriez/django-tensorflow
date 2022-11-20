# Generated by Django 4.0.5 on 2022-11-20 16:42

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_customer_head_3_customer_head_4_customer_head_5'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='second_base_1',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
        migrations.AddField(
            model_name='customer',
            name='second_base_2',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
        migrations.AddField(
            model_name='customer',
            name='second_base_3',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
        migrations.AddField(
            model_name='customer',
            name='second_base_4',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
        migrations.AddField(
            model_name='customer',
            name='second_base_5',
            field=models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path),
        ),
    ]