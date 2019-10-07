from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Session
from django.views import generic
from django.contrib import messages


# Generic survey view displaying a list of all surveys
class SurveysView(generic.ListView):
    model = Survey

# Generic Detail View for a Surveys
class SurveyDetailView(generic.DetailView):
    model = Survey

class SurveyDeleteView(generic.DeleteView):
    model = Survey

class SurveyCreateView(generic.CreateView):
    model = Survey
    fields = [
        'name',
        'description',
    ]

class SurveyUpdateView(generic.UpdateView):
    model = Survey
    fields = [
        'name',
        'description',
        'introduction'
    ]

def delete_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Survey successfully deleted')
        return redirect('surveys:surveys')
