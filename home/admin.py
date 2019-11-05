from django.contrib import admin
from .models import Post
from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    pass
