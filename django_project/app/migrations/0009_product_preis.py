# Generated by Django 3.2.7 on 2021-12-12 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_termine_datum'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='preis',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
