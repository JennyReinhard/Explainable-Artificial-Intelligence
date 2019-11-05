from django.contrib import admin
from .models import Survey, Session, SetFactor, SetLevel, Trial
from import_export.admin import ImportExportModelAdmin

# Register your models here.
# admin.site.register(Survey)
admin.site.register(Session)
# admin.site.register(SetLevel)
# admin.site.register(SetFactor)
admin.site.register(Trial)

@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin):
    pass

@admin.register(SetFactor)
class SurveySetFactor(ImportExportModelAdmin):
    pass

@admin.register(SetLevel)
class SurveySetLevel(ImportExportModelAdmin):
    pass
