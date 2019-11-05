from django import forms
from .models import Survey, Session

class SurveyCreateFrom(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            'name',
            'description',
            'introduction',
            'ready',
        ]

class ParticipantIDForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'participantID',
            'comment'
        ]
