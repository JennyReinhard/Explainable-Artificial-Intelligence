from django import forms
from .models import Survey

class SurveyCreateFrom(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            'name',
            'description',
            'introduction',
            'ready'
        ]
