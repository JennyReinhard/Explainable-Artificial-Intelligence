# Generated by Django 3.0.3 on 2021-07-06 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20210707_0005'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='content',
            new_name='content_de',
        ),
    ]
