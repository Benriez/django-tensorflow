# Generated by Django 4.0.5 on 2022-11-06 17:35

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=30, null=True, unique=True)),
                ('offer_pdf', models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path)),
                ('extra_pdf', models.FileField(blank=True, null=True, storage=app.models.PDFStorage(), upload_to=app.models.get_upload_path)),
                ('success', models.BooleanField(default=False)),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Erstellt am')),
                ('anrede', models.CharField(max_length=10, null=True)),
                ('vorname', models.CharField(max_length=30, null=True)),
                ('nachname', models.CharField(max_length=30, null=True)),
                ('plz', models.CharField(max_length=8, null=True)),
                ('ort', models.CharField(max_length=30, null=True)),
                ('strasse', models.CharField(max_length=30, null=True)),
                ('hausnr', models.CharField(max_length=30, null=True)),
                ('iban', models.BinaryField(default=b'\x08')),
                ('birthdate', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StandardPDF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('pdf', models.FileField(blank=True, null=True, storage=app.models.StandardPDFStorage(), upload_to=app.models.get_standard_upload_path)),
            ],
        ),
    ]
