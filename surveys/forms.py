from django import forms
from .models import Survey, Session

# Form for creating a Survey
class SurveyCreateFrom(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            'name',
            'description',
            'introduction',
            'ready',
        ]
# Form for saving a participants ID and comment at the end of the survey
class ParticipantIDForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'participantID',
            'comment'
        ]
