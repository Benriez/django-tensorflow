# Generated by Django 4.0.5 on 2022-11-05 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_customer_anrede_customer_hausnr_customer_iban_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='birthdate',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='iban',
            field=models.CharField(max_length=50, null=True),
        ),
    ]