# Generated by Django 3.0.3 on 2021-07-06 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='content_de',
        ),
        migrations.RemoveField(
            model_name='post',
            name='content_en',
        ),
        migrations.RemoveField(
            model_name='post',
            name='title_de',
        ),
        migrations.RemoveField(
            model_name='post',
            name='title_en',
        ),
    ]
