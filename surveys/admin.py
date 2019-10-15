from django.contrib import admin
from .models import Survey, Session, SetFactor, SetLevel, Trial

# Register your models here.
admin.site.register(Survey)
admin.site.register(Session)
admin.site.register(SetLevel)
admin.site.register(SetFactor)
admin.site.register(Trial)
