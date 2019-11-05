from django.contrib import admin
from .models import Survey, Session, SetFactor, SetLevel, Trial, Redirect
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
class SetFactorAdmin(ImportExportModelAdmin):
    pass

@admin.register(SetLevel)
class SetLevelAdmin(ImportExportModelAdmin):
    pass

@admin.register(Redirect)
class RedirectAdmin(ImportExportModelAdmin):
    pass
