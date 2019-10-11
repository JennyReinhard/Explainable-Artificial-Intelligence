from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Session, Redirect, SetFactor, SetLevel
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from .set import Set, showRandomSet


# Generic survey view displaying a list of all surveys
class SurveysView(LoginRequiredMixin,generic.ListView):
    model = Survey

# Generic detail View for a Surveys
class SurveyDetailView(LoginRequiredMixin, generic.DetailView):
    model = Survey

class SurveyUptateView(LoginRequiredMixin, generic.UpdateView):
    model = Survey
    fields = [
        'name',
        'description',
        'introduction',
        'ready'
    ]

# Generic create view to create a new survey
def create_survey(request):
    if request.method == 'POST':
        form = SurveyCreateFrom(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, 'New survey successfully created.')
            return redirect('surveys:survey', pk=instance.id )
    else:
        form = SurveyCreateFrom()
        context = {
            'form': form
        }
    return render(request, 'surveys/survey_form.html', context)

# View function that deletes a survey
def delete_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)

    if survey.user != request.user or request.user != 'admin':
        raise PermissionDenied

    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Survey successfully deleted')
        return redirect('surveys:surveys')

def delete_sessions(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    Session.objects.filter(survey=survey).all().delete()
    messages.success(request, 'Sessions deleted')
    return redirect('surveys:survey', pk=pk)

def start_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    try:
        redirect = survey.redirect_set.get(purpose=0)
    except ObjectDoesNotExist:
        redirect = None

    blockfactors = SetFactor.objects.filter(survey=survey, blockfactor=True)
    blockfactors_list = []
    for blockfactor in blockfactors:
        blockfactors_list.append(list(SetLevel.objects.filter(set_factor=blockfactor)))

    trialfactors = SetFactor.objects.filter(survey=survey, blockfactor=False)
    trialfactors_list =[]
    for trialfactor in trialfactors:
        trialfactors_list.append(list(SetLevel.objects.filter(set_factor=trialfactor)))

    set = Set(blockfactors_list, trialfactors_list)

    showRandomSet(set)

    request.session.flush()
    request.session.create()
    session_key = request.session.session_key
    client_ip = '127.0.0.1'
    session = Session(survey=survey, key=session_key, ip_address=client_ip)
    session.save()

    context = {
        'survey': survey,
        'session': session,
        'redirect': redirect,
    }

    return render(request, 'surveys/start_survey.html', context)

def survey_ready(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    context = {
        'survey': survey,
        'session': session,
        'error_message': 'Wrong session key'
    }
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', context)

    return render(request, 'surveys/survey_ready.html', context )
#404 handler
def handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)

#500 handler
def handler500(request, *args, **kwargs):
    return render(request, '500.html', status=500)
