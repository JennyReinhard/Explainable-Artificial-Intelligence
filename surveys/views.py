from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied

from .set import Set
from .models import Survey, Session, Redirect, SetFactor, SetLevel
from .forms import SurveyCreateFrom

import pickle
import json
import os


# Generic survey view displaying a list of all surveys
class SurveysView(LoginRequiredMixin,generic.ListView):
    model = Survey

# Generic detail view for a Surveys
class SurveyDetailView(LoginRequiredMixin, generic.DetailView):
    model = Survey

# Generic update view for surveys
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
            # Links current user to the survey on creation
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

    # Checks if user can delete the survey
    if survey.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Survey successfully deleted')
        return redirect('surveys:surveys')
# Deletes all sessions in a survey
def delete_sessions(request, pk):
    survey = get_object_or_404(Survey, pk=pk)

    if survey.user != request.user:
        raise PermissionDenied
    Session.objects.filter(survey=survey).all().delete()
    messages.success(request, 'Sessions deleted')
    return redirect('surveys:survey', pk=pk)

# Returns survey start screen
def start_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    # if there is a redirect, redirect
    try:
        redirect_obj = survey.redirect_set.get(purpose=0)
    except ObjectDoesNotExist:
        redirect_obj = None

    context = {
        'survey': survey,
        'redirect': redirect_obj
    }

    return render(request, 'surveys/start_survey.html', context)

# Loads sets through ajax call while start_survey.html is loading
def load_set(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    # Get blockfactors for survey and store them in a list
    blockfactors = SetFactor.objects.filter(survey=survey, blockfactor=True)
    blockfactors_list = []
    for blockfactor in blockfactors:
        blockfactors_list.append(list(SetLevel.objects.filter(set_factor=blockfactor)))

    # Get trialfactors for survey and store them in a list
    trialfactors = SetFactor.objects.filter(survey=survey, blockfactor=False)
    trialfactors_list =[]
    for trialfactor in trialfactors:
        trialfactors_list.append(list(SetLevel.objects.filter(set_factor=trialfactor)))

    # if there are any trial factors, create set
    if trialfactors:
        set = Set(blockfactors_list, trialfactors_list)
    else:
        error_message = "No trial factors found for the current survey"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    # Flushes session and create new one
    request.session.flush()
    request.session.create()

    # Saves session with session information
    session_key = request.session.session_key
    client_ip = get_ip(request)
    session = Session(survey=survey, key=session_key, ip_address=client_ip)
    session.save()

    #saves set to pickle to ensure object persistency
    with open('sessions/set_'+session.key, 'wb') as f:
        pickle.dump(set, f)

    # data that is returned to ajax call
    data = {}
    data['session_key'] = session.key

    return HttpResponse(json.dumps(data), content_type='application/json')

# Renders screen before trials start.
def survey_ready(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    context = {
        'survey': survey,
        'session': session,
    }

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    return render(request, 'surveys/survey_ready.html', context )

def trial(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    # Open set through pockle
    with open('sessions/set_'+session.key, 'rb') as f:
        set = pickle.load(f)

    # If there is no current set, render error message
    if not set:
        error_message = "No current set available to work with, try and start a new survey"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    #While there are tables on the stack, fetch them
    if not set.isEmpty() and set.top().size() >= 1:
        #returns first trial of first block
        trial = set.top().top()

    #if no more tables on the stack, pop block and redirect
    elif not set.isEmpty() and set.top().isEmpty():
        #pops the set and saves it to pickle
        set.pop()
        with open('sessions/set_'+session.key, 'wb') as f:
            pickle.dump(set, f)

        # If they are redirects, redirect, otherwise go to next block
        try:
            redirect_obj = survey.redirect_set.get(purpose=1)
            return redirect(redirect_obj.url)
        except ObjectDoesNotExist:
            return redirect('surveys:trial', survey_id = survey_id, session_key=session_key)

    #if set is totally empty redirect to
    elif set.isEmpty():
        # Remove saved session files
        os.remove('sessions/set_'+session.key)
        os.remove('pickle/training_set_'+session.key)

        #if there is a redirect, redirect, otherwise go to home
        try:
            redirect_obj = survey.redirect_set.get(purpose=2)
            return redirect(redirect_obj.url+"?sessionkey="+session.key)

        except ObjectDoesNotExist:
            return redirect('home:home')

    size = set.top().size()
    progress = 12 - size

    context = {
        'set':set,
        'dss_slug': trial.dss.slug,
        'dss_name': trial.dss.name,
        'errors': trial.errors,
        'attempts': trial.attempts,
        'reliability': trial.reliability,
        'size': size,
        'progress': progress,
        'session': session,
        'survey': survey,
    }

    return render(request, 'surveys/trial.html', context )

# Saves trial
def save_trial(request):
    if request.method == 'POST':
        # Loads saved session set
        with open('sessions/set_'+request.session.session_key, 'rb') as f:
            set = pickle.load(f)

        if not set.blocks[-1].isEmpty():
            # Pops the highest block
            set.top().pop()
            with open('sessions/set_'+request.session.session_key, 'wb') as f:
                pickle.dump(set, f)

    return HttpResponse('success')

#404 handler
def handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)

#500 handler
def handler500(request, *args, **kwargs):
    return render(request, '500.html', status=500)

# Helper function that gets the IP of the participant
def get_ip(request):
    try:
        x_forward = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forward:
            ip = x_forward.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    except:
        ip = ''
    return ip
