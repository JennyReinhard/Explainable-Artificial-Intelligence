from modeltranslation.translator import register, TranslationOptions
from .models import Post

# Register Post for translation
@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
