# Generated by Django 3.2.7 on 2021-12-11 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_customer_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=32)),
            ],
        ),
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Kunde', 'verbose_name_plural': 'Kunden'},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auftragstyp', models.CharField(blank=True, max_length=128, null=True, verbose_name='Auftragstyp')),
                ('menge', models.IntegerField(default=0)),
                ('comment', models.TextField(blank=True, max_length=1000, verbose_name='Kommentar')),
                ('produkt', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.product')),
            ],
        ),
    ]
