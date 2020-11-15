from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.utils.translation import get_language
from .set import Set, showSet
from .models import Survey, Session, Redirect, SetFactor, SetLevel, Trial
from .forms import SurveyCreateFrom, ParticipantIDForm
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg,Sum

import urllib.parse
from itertools import islice
import random

import pickle
import json
import os


# Generic survey view displaying a list of all surveys
class SurveysView(LoginRequiredMixin,generic.ListView):
    model = Survey


# Generic update view for surveys
class SurveyUptateView(LoginRequiredMixin, generic.UpdateView):
    model = Survey
    fields = [
        'name',
        'description',
        'introduction',
        'ready',
        'end'
    ]


# Generic detail view for a Surveys
def survey_detail(request, pk):
    survey = get_object_or_404(Survey, pk=pk)

    trials = Trial.objects.filter(sessionkey__survey=survey)
    ntrials = len(trials)


    context = {
        'survey': survey,
        'ntrials': ntrials
    }

    return render(request, 'surveys/survey_detail.html', context)

# Generates detailed view of sessions
def session_detail(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # Gets all trials for that the requested session
    trials = Trial.objects.filter(sessionkey=session)


    context = {
        'survey': survey,
        'session': session,
    }
    return render(request, 'surveys/session_detail.html', context)


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
def introduction(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    # if there is a redirect, redirect
    try:
        redirect_url = survey.redirect_set.get(purpose=0).url

    # else set redirect to None
    except ObjectDoesNotExist:
        redirect_url = None

    context = {
        'survey': survey,
        'redirect': redirect_url,
    }

    return render(request, 'surveys/introduction.html', context)

# Loads sets through ajax call while start_survey.html is loading
def load_set(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    language = get_language()

    #Gets trial multiplicator and training count
    ntrials = survey.ntrials
    ntraining = survey.ntraining

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
    if trialfactors or blockfactors:
        set = Set(blockfactors_list, trialfactors_list, ntrials, ntraining)

    else:
        error_message = "No trial factors found for the current survey"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'survey':survey})

    # Flushes session and create new one
    request.session.flush()
    request.session.create()

    # Saves session with session information
    session_key = request.session.session_key
    client_ip = get_ip(request)
    session = Session(survey=survey, key=session_key, ip_address=client_ip)
    session.save()

    #saves set to pickle to ensure object persistency
    try:
        with open('sessions/set_'+session.key, 'wb') as f:
            pickle.dump(set, f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    # data that is returned to ajax call
    data = {}
    data['session_key'] = session.key
    data['language'] = language
    data['ipaddress'] =  session.ip_address
    print("got here")
    return HttpResponse(json.dumps(data), content_type='application/json')

# Renders screen before trials start.
def instructions(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})

    context = {
        'survey': survey,
        'session': session,
    }

    return render(request, 'surveys/instructions.html', context )

def training(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)
    language = get_language()

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    # Open set through pockle
    try:
        with open('sessions/set_'+session.key, 'rb') as f:
            set = pickle.load(f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    # If there is no current set, render error message
    if not set:
        error_message = "No current set available to work with, try and start a new survey"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    # if training counter not 0, choose another training
    if set.ntraining > 0:
        block = random.choice(set.blocks)
        trial = random.choice(block.trials)

    else:
        return redirect('surveys:survey-ready', survey_id=survey.id, session_key=session.key)

    context = {
        'session': session,
        'survey': survey,
        'language': language,
    }

    # decrease training counter
    set.ntraining = set.ntraining - 1

    # save set to pickle file
    try:
        with open('sessions/set_'+session.key, 'wb') as f:
            pickle.dump(set, f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    return render(request, 'surveys/training.html', context)

def save_training(request, survey_id, session_key):
    if request.method == 'POST':
        # try to open pickle file
        try:
            with open('sessions/set_'+ session_key, 'rb') as f:
                set = pickle.load(f)
        except:
            return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

        # Try to save pickle file
        try:
            with open('sessions/set_'+session_key, 'wb') as f:
                pickle.dump(set, f)
        except:
            return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

        return HttpResponse('success')

    return HttpResponse('fail')

def survey_ready(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    #If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    # try to open set through picke file
    try:
        with open('sessions/set_'+session.key, 'rb') as f:
            set = pickle.load(f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    context = {
        'survey': survey,
        'session': session,
    }

    return render(request, 'surveys/survey_ready.html', context)

def trial(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)
    language = get_language()

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    # Open set through pockle
    try:
        with open('sessions/set_'+session.key, 'rb') as f:
            set = pickle.load(f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    # If there is no current set, render error message
    if not set:
        error_message = "No current set available to work with, try and start a new survey"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    #While there are tables on the stack, fetch them
    if not set.isEmpty() and set.top().size() >= 1:
        #returns first trial of first block
        trial = set.top().top()
        #returns firs block
        block = set.top()

    #if no more tables on the stack, pop block and redirect
    elif not set.isEmpty() and set.top().isEmpty():
        #pops the set and saves it to pickle
        block = set.top()

        # Checks if there is a intermediate redirect
        try:
            redirect_url = survey.redirect_set.get(purpose=1).url+'?sessionkey='+session.key+'&surveyid='+str(survey.id)+'&balance='+str(block.balance)+'&language='+str(language)+'&dss='+urllib.parse.quote(block.dss.name)+'&blockcounter='+str(block.blockcounter)
            redirect_url = redirect_url+'&scenario='+urllib.parse.quote(block.scenario.name)+'&injuries='+str(block.injuries)+'&max='+str(block.max)+'&Q_Language='+language.upper()
        # else returns to next trial
        except ObjectDoesNotExist:
            redirect_url = reverse('surveys:trial', kwargs={'survey_id': survey.id, 'session_key': session.key})

        context = {
            'sesssion':session,
            'survey':survey,
            'max': block.max,
            'redirect': redirect_url,
            'blockcounter': block.blockcounter
        }

        set.pop()

        try:
            with open('sessions/set_'+session.key, 'wb') as f:
                pickle.dump(set, f)
        except:
            return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

        return render(request, 'surveys/result.html', context)

    #if set is totally empty redirect to
    elif set.isEmpty():

        #if there is a redirect, redirect, otherwise go to home
        try:
            redirect_obj = survey.redirect_set.get(purpose=2)
            return redirect(redirect_obj.url+"?sessionkey="+session.key+'&surveyid='+str(survey.id)+'&language='+language+'&Q_Language='+language.upper())
        #else redirect to end
        except ObjectDoesNotExist:
            return redirect('surveys:end', survey_id=survey.id, session_key=session.key)

    size = set.top().size()

    # creates new database trial
    db_trial = Trial(sessionkey=session)
    db_trial.save()

    context = {
        'set':set,
        'session': session,
        'survey': survey,
        'blockcounter': block.blockcounter,
        'trial': db_trial,
        'language': language,
        'max': block.max
    }

    return render(request, 'surveys/trial.html', context )

# Saves trial
def save_trial(request, trial_id):
    if request.method == 'POST':
        sessionkey = request.POST.get('sessionkey', False)
        session = get_object_or_404(Session, key=sessionkey)

        # If session key is not current users session key, raise error
        if session.key != request.session.session_key:
            error_message = "Wrong session key"
            return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

        #gets trial
        trial = get_object_or_404(Trial, id=trial_id)

        #Gets ajax call data
        trial.blockcounter = int(request.POST.get('blockcounter', 0))
        trial.save()

        # Loads saved session set
        try:
            with open('sessions/set_'+ sessionkey, 'rb') as f:
                set = pickle.load(f)
        except:
            return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

        # Pops the highest trial
        if not set.top().isEmpty():
            set.top().pop()

            #Save set to pickle
            try:
                with open('sessions/set_'+sessionkey, 'wb') as f:
                    pickle.dump(set, f)
            except:
                return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    return HttpResponse('success')

def block_ready(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})

    language = get_language()

    #Try to load session set saved in pickle
    try:
        with open('sessions/set_'+session.key, 'rb') as f:
            set = pickle.load(f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    # if no more trials in the set, redirect to post url
    if set.isEmpty():
        try:
            redirect_url = survey.redirect_set.get(purpose=2).url+"?sessionkey="+session.key+'&surveyid='+str(survey.id)+'&language='+language+'&Q_Language='+language.upper()

        # if redirect does not exist, redirect to endscreen
        except ObjectDoesNotExist:
            redirect_url = reverse('surveys:end')

        return redirect(redirect_url)

    context = {
        'survey': survey,
        'session': session,
    }

    return render(request, 'surveys/block_ready.html', context )

def end(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})

    if request.method == 'POST':
        form = ParticipantIDForm(request.POST or None, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully finished and deleted session')
            #renoves the pickled set
            os.remove('sessions/set_'+session.key)
            #redirects to index
            return redirect('home:index')
    else:
        form = ParticipantIDForm(instance=session)
        context = {
            'session': session,
            'survey': survey,
            'form': form
        }

    return render(request, 'surveys/end.html', context)

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
