# Generated by Django 3.0.3 on 2021-07-06 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0023_auto_20210704_2200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setlevel',
            name='name_de',
        ),
        migrations.RemoveField(
            model_name='setlevel',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='end_de',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='end_en',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='introduction_de',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='introduction_en',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='name_de',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='ready_de',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='ready_en',
        ),
    ]
