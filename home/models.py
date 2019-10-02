from django.db import models

# Create your models here.
class Post(models.Model):
    name = models.CharField(max_length=70)
    content = models.TextField()
    purpose = models.CharField(max_length=70)
    created = models.DateTimeField(auto_now=True)
    
