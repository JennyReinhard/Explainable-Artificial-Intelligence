from django import forms
from .models import Survey

class SurveyCreateFrom(forms.ModelForm):

    class Meta:
        model = Survey
        fields = [
            'name',
            'description'
        ]
        
class SurveyUpdateForm(forms.ModelForm):

    class Meta:
        model = Survey
        fields = [
            'name',
            'description',
            'introduction'
        ]
