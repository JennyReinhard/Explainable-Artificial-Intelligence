from modeltranslation.translator import register, TranslationOptions
from .models import Survey, SetLevel

# Registers Survey for translation
@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ('name', 'introduction', 'ready', 'end')

# Register SetLevels for translation
@register(SetLevel)
class SetLevelTranslationOptions(TranslationOptions):
    fields = ('name',)
