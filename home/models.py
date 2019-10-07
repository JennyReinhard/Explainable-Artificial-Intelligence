from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse

# Create your models here.
class Post(models.Model):
    POST_TYPES = [
        ('HOMEPAGE', 'Homepage'),
        ('POST', 'Post or Blogpost'),
        ('PAGE', 'Page')
    ]
    title = models.CharField(max_length=70)
    content = HTMLField()
    created = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=70, choices=POST_TYPES, default='PAGE')

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('home:index')
