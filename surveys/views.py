from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.utils.translation import get_language
from .set import Set, showFailTrials, showSet
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

# Generic detail view for a Surveys
def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    trials = Trial.objects.filter(sessionkey__survey=survey)
    ntrials = len(trials)

    context = {
        'survey': survey,
        'ntrials': ntrials
    }

    return render(request, 'surveys/survey_detail.html', context)

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
def session_detail(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    trials = Trial.objects.filter(sessionkey=session)
    total_injuries = 0
    for trial in trials:
        total_injuries = total_injuries + trial.injuries

    if trials:
        avgTrialDuration = round(trials.aggregate(Avg('trialDuration')).get('trialDuration__avg', 0)/1000,2)
        avgFeedBackDuration = round(trials.aggregate(Avg('feedbackDuration')).get('feedbackDuration__avg', 0)/1000, 2)
        totalDuration = round(trials.aggregate(Sum('trialDuration')).get('trialDuration__sum', 0)/60000, 2)

    else:
        avgTrialDuration = "No trials yet"
        avgFeedBackDuration = "No trials yet"
        totalDuration = "No trials yet"


    context = {
        'survey': survey,
        'session': session,
        'injuries': total_injuries,
        'avgTrialDuration': avgTrialDuration,
        'avgFeedBackDuration': avgFeedBackDuration,
        'totalTrialDuration': totalDuration
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
            return redirect('surveys:survey', survey_id=instance.id )
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
    print(language)
    #Gets trial multiplicator
    ntrials = survey.ntrials

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
        set = Set(blockfactors_list, trialfactors_list, ntrials, 3)

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
    with open('sessions/set_'+session.key, 'wb') as f:
        pickle.dump(set, f)

    # data that is returned to ajax call
    data = {}
    data['session_key'] = session.key
    data['language'] = language

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

def block_ready(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)
    language = get_language()



    with open('sessions/set_'+session.key, 'rb') as f:
        set = pickle.load(f)

    if set.isEmpty():
        try:
            redirect_url = survey.redirect_set.get(purpose=2).url+"?sessionkey="+session.key+'&surveyid='+str(survey.id)+'&language='+language+'&Q_Language='+language.upper()

        except ObjectDoesNotExist:
            redirect_url = reverse('surveys:end')
        return redirect(redirect_url)

    context = {
        'survey': survey,
        'session': session,
    }

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})

    return render(request, 'surveys/block_ready.html', context )


def survey_ready(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    try:
        with open('sessions/set_'+session.key, 'rb') as f:
            set = pickle.load(f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    #If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    context = {
        'survey': survey,
        'session': session,
        'injuries': set.training_injuries,
        'balance': set.training_balance
    }

    return render(request, 'surveys/survey_ready.html', context)

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

    if set.training_counter > 0:
        block = random.choice(set.blocks)
        trial = random.choice(block.trials)

    else:
        return redirect('surveys:survey-ready', survey_id=survey.id, session_key=session.key)

    context = {
        'dss': trial.dss,
        'risk': trial.risk,
        'errors': trial.errors,
        'attempts': trial.attempts,
        'reliability': trial.reliability,
        'scenario': trial.scenario,
        'package': trial.package,
        'manual': trial.manual,
        'suggestion': trial.suggestion,
        'best_choice': trial.best_choice,
        'success': trial.success,
        'balance': set.training_balance,
        'injuries': set.training_injuries,
        'session': session,
        'survey': survey,
        'language': language,
    }

    set.training_counter = set.training_counter - 1
    with open('sessions/set_'+session.key, 'wb') as f:
        pickle.dump(set, f)



    return render(request, 'surveys/training.html', context)

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
        block = set.top()

    #if no more tables on the stack, pop block and redirect
    elif not set.isEmpty() and set.top().isEmpty():
        #pops the set and saves it to pickle
        block = set.top()
        try:
            redirect_url = survey.redirect_set.get(purpose=1).url+'?sessionkey='+session.key+'&surveyid='+str(survey.id)+'&balance='+str(block.balance)+'&language='+str(language)+'&dss='+urllib.parse.quote(block.dss.name)+'&blockcounter='+str(block.blockcounter)
            redirect_url = redirect_url+'&scenario='+urllib.parse.quote(block.scenario.name)+'&injuries='+str(block.injuries)+'&max='+str(block.max)+'&Q_Language='+language.upper()
        except ObjectDoesNotExist:
            redirect_url = reverse('surveys:trial', kwargs={'survey_id': survey.id, 'session_key': session.key})

        context = {
            'sesssion':session,
            'survey':survey,
            'dss': block.dss.name,
            'scenario': block.scenario.name,
            'balance': block.balance,
            'injuries': block.injuries,
            'max': block.max,
            'redirect': redirect_url,
            'blockcounter': block.blockcounter
        }

        set.pop()
        with open('sessions/set_'+session.key, 'wb') as f:
            pickle.dump(set, f)

        return render(request, 'surveys/result.html', context)

    #if set is totally empty redirect to
    elif set.isEmpty():


        #if there is a redirect, redirect, otherwise go to home
        try:
            redirect_obj = survey.redirect_set.get(purpose=2)
            return redirect(redirect_obj.url+"?sessionkey="+session.key+'&surveyid='+str(survey.id)+'&language='+language+'&Q_Language='+language.upper())

        except ObjectDoesNotExist:
            return redirect('surveys:end', survey_id=survey.id, session_key=session.key)

    size = set.top().size()
    progress = 12 - size

    db_trial = Trial(sessionkey=session)
    db_trial.save()

    context = {
        'set':set,
        'dss': trial.dss,
        'risk': trial.risk,
        'errors': trial.errors,
        'attempts': trial.attempts,
        'reliability': trial.reliability,
        'scenario': trial.scenario,
        'package': trial.package,
        'manual': trial.manual,
        'suggestion': trial.suggestion,
        'best_choice': trial.best_choice,
        'success': trial.success,
        'balance': block.balance,
        'injuries': block.injuries,
        'size': size,
        'progress': progress,
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
        trial = Trial.objects.get(id=trial_id)
        trial.reliability = int(request.POST.get('reliability', False))
        trial.dss = request.POST.get('dss', False)
        trial.risk = request.POST.get('risk', False)
        trial.scenario = request.POST.get('scenario', False)
        trial.package_value = int(request.POST.get('package_value', False))
        trial.attempts = int(request.POST.get('attempts', False))
        trial.errors = int(request.POST.get('errors', False))
        if request.POST.get('success') == 'True':
            trial.success = True
        elif request.POST.get('success') == 'False':
            trial.success = False
        else:
            trial.success = None
        trial.suggestion = request.POST.get('suggestion', False)
        trial.best_choice = request.POST.get('best_choice', False)
        trial.blockcounter = int(request.POST.get('blockcounter', False))
        trial.decision = request.POST.get('decision', False)
        trial.trialDuration = int(request.POST.get('trialDuration', False))
        trial.injuries = int(request.POST.get('injuries', 0))
        trial.save()

        # Loads saved session set
        with open('sessions/set_'+ sessionkey, 'rb') as f:
            set = pickle.load(f)

        if not set.blocks[-1].isEmpty():
            # Pops the highest block
            profit = int(request.POST.get('profit', None))
            injuries = int(request.POST.get('injuries', None))
            package_value = int(request.POST.get('package_value', None))
            manual_labour = int(request.POST.get('manual_labour', None))
            set.top().balance = set.top().balance + profit
            set.top().injuries = set.top().injuries + injuries
            set.top().pop()
            with open('sessions/set_'+sessionkey, 'wb') as f:
                pickle.dump(set, f)

    return HttpResponse('success')

def save_feedback(request, trial_id):
    if request.method == 'POST':
        trial = Trial.objects.get(id=trial_id)
        trial.feedbackDuration = int(request.POST.get('feedbackDuration', False))
        trial.profit = int(request.POST.get('profit', 0))
        print(trial.profit)
        print(trial.feedbackDuration)
        trial.save()
        return HttpResponse('success')

    return HttpResponse('fail')

def save_training(request, survey_id, session_key):
    if request.method == 'POST':
        with open('sessions/set_'+ session_key, 'rb') as f:
            set = pickle.load(f)

        profit = int(request.POST.get('profit', None))
        injuries = int(request.POST.get('injuries', None))
        set.training_balance = set.training_balance + profit
        set.training_injuries = set.training_injuries + injuries
        print(set.training_balance)

        with open('sessions/set_'+session_key, 'wb') as f:
            pickle.dump(set, f)

        return HttpResponse('success')

    return HttpResponse('fail')

def end(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    if request.method == 'POST':
        form = ParticipantIDForm(request.POST or None, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully finished and deleted session')
            # os.remove('sessions/set_'+session.key)
            return redirect('home:index')
    else:
        form = ParticipantIDForm(instance=session)
        context = {
            'session': session,
            'survey': survey,
            'form': form
        }

    return render(request, 'surveys/end.html', context)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})
    # Remove saved session files
    os.remove('sessions/set_'+session.key)

    return render(request,'surveys/end.html', context)

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

class Sessions(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, session_key):

        session = get_object_or_404(Session, key=session_key)
        trials = [trial.id for trial in Trial.objects.filter(sessionkey=session)]
        feedbackTimes = [trial.feedbackDuration for trial in Trial.objects.filter(sessionkey=session)]
        trialTimes = [trial.trialDuration for trial in Trial.objects.filter(sessionkey=session)]

        data = {
            'trials': trials,
            'feedbackDuration': feedbackTimes,
            'trialDuration': trialTimes
        }
        return Response(data)

class Surveys(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, pk=survey_id)
        trials = Trial.objects.filter(sessionkey__survey=survey)
        scenario_comparison = [
            trials.filter(scenario='medical').aggregate(Avg('trialDuration')).get('trialDuration__avg', 'No average trial duration'),
            trials.filter(scenario='urban').aggregate(Avg('trialDuration')).get('trialDuration__avg', 'No average trial duration'),
            trials.filter(scenario='warehouse').aggregate(Avg('trialDuration')).get('trialDuration__avg', 'No average trial duration')
        ]

        data = {
            'scenario_comparison': scenario_comparison
        }

        return Response(data)
