# Generated by Django 4.0.5 on 2022-11-04 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_standardpdf_delete_standardpdfs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='extra_pdf',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='offer_pdf',
        ),
    ]
