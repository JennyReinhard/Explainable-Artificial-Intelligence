# Generated by Django 3.0.3 on 2021-05-17 09:46

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0009_auto_20191011_1323'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='redirect',
            options={'ordering': ['purpose']},
        ),
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ['-start_date']},
        ),
        migrations.AddField(
            model_name='session',
            name='comment',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='participantID',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='setlevel',
            name='name_de',
            field=models.CharField(max_length=255, null=True, verbose_name='Factor Name'),
        ),
        migrations.AddField(
            model_name='setlevel',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Factor Name'),
        ),
        migrations.AddField(
            model_name='survey',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='end',
            field=tinymce.models.HTMLField(blank=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='end_de',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='end_en',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='introduction_de',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='introduction_en',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='name_de',
            field=models.CharField(help_text='Give survey a name', max_length=255, null=True, verbose_name='The surveys name'),
        ),
        migrations.AddField(
            model_name='survey',
            name='name_en',
            field=models.CharField(help_text='Give survey a name', max_length=255, null=True, verbose_name='The surveys name'),
        ),
        migrations.AddField(
            model_name='survey',
            name='ntraining',
            field=models.IntegerField(default=3, verbose_name='Training number'),
        ),
        migrations.AddField(
            model_name='survey',
            name='ntrials',
            field=models.IntegerField(default=1, verbose_name='Trial multiplicator'),
        ),
        migrations.AddField(
            model_name='survey',
            name='ready_de',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='survey',
            name='ready_en',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='end_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='setlevel',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Factor Name'),
        ),
        migrations.AlterField(
            model_name='setlevel',
            name='value',
            field=models.IntegerField(verbose_name='Factor value'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='Trial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blockcounter', models.IntegerField(null=True)),
                ('sessionkey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.Session')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
