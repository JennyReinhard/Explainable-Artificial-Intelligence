from modeltranslation.translator import register, TranslationOptions
from .models import Survey

@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ('name', 'introduction', 'ready')
