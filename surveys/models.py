from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse

# Create your models here.
class Survey(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='The surveys name',
        help_text="Give survey a name"
    )

    description = models.TextField(
        verbose_name='Short description of the survey',
        help_text='Give the survey a short description, so that others know what it us'
    )

    date_created = models.DateTimeField(auto_now=True)
    introduction = HTMLField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('surveys:survey', kwargs={'pk':self.pk})

class Session(models.Model):
    key = models.CharField(max_length=255, primary_key=True)

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='Related survey')

    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        protocol = 'both',
        unpack_ipv4=True
    )
