from django.contrib import admin
from .models import Survey, Session, SetFactor, SetLevel, Trial, Redirect
from import_export.admin import ImportExportModelAdmin

# Registers Survey for import and export
@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin):
    pass
# Registers SetFactor for import and export
@admin.register(SetFactor)
class SetFactorAdmin(ImportExportModelAdmin):
    pass

# Registers SetLevel for import and export
@admin.register(SetLevel)
class SetLevelAdmin(ImportExportModelAdmin):
    pass

# Registers Redirect for import and export
@admin.register(Redirect)
class RedirectAdmin(ImportExportModelAdmin):
    pass

# Registers Session for import and export
@admin.register(Session)
class SessionAdmin(ImportExportModelAdmin):
    pass

# Registers Trial for import and export
@admin.register(Trial)
class TrialAdmin(ImportExportModelAdmin):
    pass
