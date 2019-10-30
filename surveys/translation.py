from modeltranslation.translator import register, TranslationOptions
from .models import Survey, SetLevel

@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ('name', 'introduction', 'ready')

@register(SetLevel)
class SetLevelTranslationOptions(TranslationOptions):
    fields = ('name',)
