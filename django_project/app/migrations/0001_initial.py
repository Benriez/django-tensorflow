# Generated by Django 3.2.7 on 2022-06-17 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Filename')),
                ('website', models.CharField(blank=True, max_length=50, null=True, verbose_name='Website')),
                ('comment', models.TextField(blank=True, max_length=1000, verbose_name='Comment')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
    ]
