from django.contrib import admin
from .models import Survey, Session, SetFactor, SetLevel, Trial, Redirect
from import_export.admin import ImportExportModelAdmin

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

@admin.register(Session)
class SessionAdmin(ImportExportModelAdmin):
    pass

@admin.register(Trial)
class TrialAdmin(ImportExportModelAdmin):
    pass
