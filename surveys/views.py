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

from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.svm import LinearSVC
import csv

import urllib.parse
from itertools import islice
import random

import pickle
import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axislines import AxesZero
import numpy as np

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
    #try:
       # redirect_url = survey.redirect_set.get(purpose=0).url

    # else set redirect to None
    #except ObjectDoesNotExist:
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
        print(set)
    else:
        response = HttpResponse('Ressource <Set> could not be found', status=404)
        return response

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

    global i
    i = 0

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

def instructions2(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})

    context = {
        'survey': survey,
        'session': session,
    }

    return render(request, 'surveys/instructions2.html', context )

def testround(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})
    
    contextRandom = random.choice(["Immobilienpreis", "Kleidergroesse"]) 
    aimethodRandom = random.choice(["knn", "svm"])
    explanationRandom = random.choice(["Textuell", "Visuell", "Beispielbasiert"])

    #implementation of ai methods

    def make_meshgrid(x, y, h=.5):
        x_min, x_max = x.min() - 1, x.max() + 1
        y_min, y_max = y.min() - 1, y.max() + 1
        
        xx, yy = np.meshgrid(np.arange(65, 126, h),np.arange(65, 135, h))
        return xx, yy

    def plot_contours(ax, clf, xx, yy, **params):
          
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])              
        Z = Z.reshape(xx.shape)

        if contextRandom == "Immobilienpreis":
            xx = ((xx-22)**1.14)
            yy = (yy/10)-5
            print(yy)

        out = ax.contourf(xx, yy, Z, **params)
        return out

    height = []
    bust = []
    waist = []
    hips =[]
    size=[]
    sizeInt =[]

    #read data
    with open('surveys/data_clothes_neu.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=';')
        for row in csv_reader:
            height.append(int(row[0]))
            bust.append(int(row[1]))
            waist.append(int(row[2]))
            hips.append(int(row[3]))
            size.append(row[4])
            sizeInt.append(row[5])

            
    features=list(zip(height, bust, waist, hips))
    features2=list(zip(bust, hips))

    #train model
    if aimethodRandom == "knn":
        model = KNeighborsClassifier(n_neighbors=25)
        clf = KNeighborsClassifier(n_neighbors=25)
        clf.fit(features2,size)
    else:
        model = svm.SVC(kernel='rbf')
        clf = svm.SVC(kernel='rbf')
        clf.fit(features2,sizeInt)
       
        X = np.array(features2) 
        y= np.array(sizeInt)

        X0, X1 = X[:, 0], X[:, 1]

        xx, yy = make_meshgrid(X0, X1)

    model.fit(features,size)
   
    data = [157,81,56,84]
    
    #get prediction
    predicted = model.predict([data])[0]

    if contextRandom == "Immobilienpreis":
        if predicted == "Small (S)":
            predicted = "< 400.000 €"
        elif predicted == "Medium (M)":
            predicted = "400.000 - 700.000 €"
        else: 
            predicted = "> 700.000 €"

    countS = 0
    countM = 0
    countL = 0
    bustNeighborS=[]
    bustNeighborM=[]
    bustNeighborL=[]
    hipsNeighborS=[]
    hipsNeighborM=[]
    hipsNeighborL=[]

    if aimethodRandom == "knn":
        neighbors = model.kneighbors([data], 25, False)

        for k in neighbors[0]:
            if size[k] == "Small (S)":
                countS += 1
            elif size[k] == "Medium (M)":
                countM += 1
            else:
                countL += 1

        neighborsImage = clf.kneighbors([[data[1],data[3]]],25,False)
        if contextRandom == "Immobilienpreis":
             for k in neighborsImage[0]:
                if size[k] == "Small (S)":
                    bustNeighborS.append(int((bust[k]-22)**1.14))
                    hipsNeighborS.append(int(hips[k]/10)-5)
                elif size[k] == "Medium (M)":
                    bustNeighborM.append(int((bust[k]-22)**1.14))
                    hipsNeighborM.append(int(hips[k]/10)-5) 
                else:
                    bustNeighborL.append(int((bust[k]-22)**1.14))
                    hipsNeighborL.append(int(hips[k]/10)-5)
        else:
     
             for k in neighborsImage[0]:
                if size[k] == "Small (S)":
                    bustNeighborS.append(bust[k])
                    hipsNeighborS.append(hips[k])
                elif size[k] == "Medium (M)":
                    bustNeighborM.append(bust[k])
                    hipsNeighborM.append(hips[k]) 
                else:
                    bustNeighborL.append(bust[k])
                    hipsNeighborL.append(hips[k])

    #plot data
    bustArrayS = []
    bustArrayM = []
    bustArrayL =[]
    hipsArrayS=[]
    hipsArrayM=[]
    hipsArrayL=[]

    l = 0

    if contextRandom == "Immobilienpreis":
        while l < len(size):
            if size[l] == "Small (S)":
                bustArrayS.append(int((bust[l]-22)**1.14))
                hipsArrayS.append(int(hips[l]/10)-5)                  
            elif size[l] == "Medium (M)":
                bustArrayM.append(int((bust[l]-22)**1.14))
                hipsArrayM.append(int(hips[l]/10)-5)
            else:
                bustArrayL.append(int((bust[l]-22)**1.14))
                hipsArrayL.append(int(hips[l]/10)-5)
            l += 1
    else:
        while l < len(size):
            if size[l] == "Small (S)":
                bustArrayS.append(bust[l])
                hipsArrayS.append(hips[l])
            elif size[l] == "Medium (M)":
                bustArrayM.append(bust[l])
                hipsArrayM.append(hips[l])
            else:
                bustArrayL.append(bust[l])
                hipsArrayL.append(hips[l])
            l += 1

    plt.ion()

    if contextRandom == "Immobilienpreis":
        if aimethodRandom == "svm":
            plt.plot(bustArrayS, hipsArrayS, 'rebeccapurple', marker= 5, markersize=7, linestyle = '')
            plt.plot(int((data[1]-22)**1.14), int(data[3]/10)-5, 'tab:red', marker = 6, markersize= 14,  linestyle = '')
            plt.plot(bustArrayM, hipsArrayM, 'darkgoldenrod', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'steelblue', marker = 4, markersize=7, linestyle = '')
        else:
            plt.plot(bustArrayS, hipsArrayS, '#d1bae8', marker= 5, markersize=7, linestyle = '')
            plt.plot(int((data[1]-22)**1.14), int(data[3]/10)-5, 'tab:red', marker = 6, markersize= 14,  linestyle = '', zorder=10)
            plt.plot(bustArrayM, hipsArrayM, '#edd498', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'lightsteelblue', marker = 4, markersize=7, linestyle = '')
            plt.plot(bustNeighborS, hipsNeighborS, 'rebeccapurple', marker= 5, markersize=10, linestyle = '')
            plt.plot(bustNeighborM, hipsNeighborM, 'darkgoldenrod', marker= 7, markersize=10, linestyle = '')
            plt.plot(bustNeighborL, hipsNeighborL, 'steelblue', marker = 4, markersize=10, linestyle = '')

        plt.xlim(80,199.99)
        plt.ylim(1.5,8.6)

        plt.xlabel('Grundstücksfläche [m²]', fontsize=14, labelpad=18, color='dimgrey')
        plt.ylabel('Zimmeranzahl', fontsize=14, labelpad=18, color='dimgrey')

        l=plt.legend(['< 400.000 €', 'Gegeben', '400.000 - 700.000 €', '> 700.000 €'],  bbox_to_anchor=(1.05, 1.15), loc='center right', framealpha=0, ncol=3, fontsize=12, columnspacing=1.5)

        l.legendHandles[1]._legmarker.set_markersize(7)
        l.legendHandles[0]._legmarker.set_color('rebeccapurple')
        l.legendHandles[2]._legmarker.set_color('darkgoldenrod')
        l.legendHandles[3]._legmarker.set_color('steelblue')

        texts=l.get_texts()
        texts[0].set_color("rebeccapurple")
        texts[2].set_color("darkgoldenrod")
        texts[3].set_color("steelblue")
        texts[1].set_color("tab:red")

    else:
        if aimethodRandom == "svm":
            plt.plot(bustArrayS, hipsArrayS, 'rebeccapurple', marker= 5, markersize=7, linestyle = '')
            plt.plot(bustArrayM, hipsArrayM, 'darkgoldenrod', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'steelblue', marker = 4, markersize=7, linestyle = '')
            plt.plot(data[1], data[3], 'tab:red', marker = 6, markersize= 14,  linestyle = '')
        else:
            plt.plot(bustArrayS, hipsArrayS, '#d1bae8', marker= 5, markersize=7, linestyle = '')
            plt.plot(bustArrayM, hipsArrayM, '#edd498', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'lightsteelblue', marker = 4, markersize=7, linestyle = '')
            plt.plot(data[1], data[3], 'tab:red', marker = 6, markersize= 14,  linestyle = '', zorder=10)
            plt.plot(bustNeighborS, hipsNeighborS, 'rebeccapurple', marker= 5, markersize=10, linestyle = '')
            plt.plot(bustNeighborM, hipsNeighborM, 'darkgoldenrod', marker= 7, markersize=10, linestyle = '')
            plt.plot(bustNeighborL, hipsNeighborL, 'steelblue', marker = 4, markersize=10, linestyle = '')

        plt.xlim(70,126.5)
        plt.ylim(70,136)
    
        plt.xlabel('Brustumfang [cm]', fontsize=14, labelpad=18, color='dimgrey')
        plt.ylabel('Hüftumfang [cm]', fontsize=14, labelpad=18, color='dimgrey')

        l=plt.legend(['Small (S)', 'Medium (M)', 'Large (L)', 'Gegeben'],  bbox_to_anchor=(1.05, 1.15), loc='center right', framealpha=0, ncol=4, fontsize=12, columnspacing=1.5)
    
        l.legendHandles[3]._legmarker.set_markersize(7)
        l.legendHandles[0]._legmarker.set_color('rebeccapurple')
        l.legendHandles[1]._legmarker.set_color('darkgoldenrod')
        l.legendHandles[2]._legmarker.set_color('steelblue')
        
        texts=l.get_texts()
        texts[0].set_color("rebeccapurple")
        texts[1].set_color("darkgoldenrod")
        texts[2].set_color("steelblue")
        texts[3].set_color("tab:red")

    plt.gcf().subplots_adjust(bottom=0.15)
    plt.gcf().subplots_adjust(left=0.15)
    plt.gcf().subplots_adjust(top=0.85)

    for ax in plt.gcf().axes:
        ax.spines['bottom'].set_color('grey')
        ax.spines['left'].set_color('grey')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(axis='x', colors='dimgrey')
        ax.tick_params(axis='y', colors='dimgrey')
        
        if contextRandom == "Immobilienpreis":            
            ax.plot((1), (1.5), ls="", marker=">", ms=10, color="dimgrey", transform=ax.get_yaxis_transform(), clip_on=False)
            ax.plot((80), (1), ls="", marker="^", ms=10, color="dimgrey", transform=ax.get_xaxis_transform(), clip_on=False)
        else:
            ax.plot((1), (70), ls="", marker=">", ms=10, color="dimgrey", transform=ax.get_yaxis_transform(), clip_on=False)
            ax.plot((70), (1), ls="", marker="^", ms=10, color="dimgrey", transform=ax.get_xaxis_transform(), clip_on=False)

        if aimethodRandom == "svm":
            plot_contours(ax, clf, xx, yy,colors=['rebeccapurple', 'dimgrey','dimgrey','darkgoldenrod', 'dimgrey','dimgrey','dimgrey','steelblue'], alpha=0.3)

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
        
    plt.savefig('surveys/static/surveys/img/visuell.png', transparent=True)

    plt.show()
    plt.close()


    context = {
        'survey': survey,
        'session': session,
        'contextRandom': contextRandom,
        'aimethodRandom': aimethodRandom,
        'explanationRandom': explanationRandom,
        'predicted': predicted,
        'countS': countS,
        'countM': countM,
        'countL': countL
    }

    return render(request, 'surveys/testround.html', context )

def testround_end(request, survey_id, session_key):
    survey = get_object_or_404(Survey, pk=survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        return render(request, 'surveys/error.html', {'error_message': 'Wrong session key', 'session':session, 'survey':survey})

    context = {
        'survey': survey,
        'session': session,
    }

    return render(request, 'surveys/testround_end.html', context )

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

i = 0

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
    
    #implementation of ai methods

    def make_meshgrid(x, y, h=.5):
        x_min, x_max = x.min() - 1, x.max() + 1
        y_min, y_max = y.min() - 1, y.max() + 1
        
        xx, yy = np.meshgrid(np.arange(65, 126, h),np.arange(65, 135, h))
        return xx, yy

    def plot_contours(ax, clf, xx, yy, **params):
          
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])              
        Z = Z.reshape(xx.shape)

        if trial.context.name == "Immobilienpreis":
            xx = ((xx-22)**1.14)
            yy = (yy/10)-5
            print(yy)

        out = ax.contourf(xx, yy, Z, **params)
        return out

    height = []
    bust = []
    waist = []
    hips =[]
    size=[]
    sizeInt=[]

    #read data
    with open('surveys/data_clothes_neu.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=';')
        for row in csv_reader:
            height.append(int(row[0]))
            bust.append(int(row[1]))
            waist.append(int(row[2]))
            hips.append(int(row[3]))
            size.append(row[4])
            sizeInt.append(row[5])

    features=list(zip(height, bust, waist, hips))
    features2=list(zip(bust, hips))

    #train model
    if trial.ai_method.name == "Nächste-Nachbarn-Klassifikation":
        model = KNeighborsClassifier(n_neighbors=25)
        clf = KNeighborsClassifier(n_neighbors=25)
        clf.fit(features2,size)
    else:
        model = svm.SVC(kernel='rbf')
        clf = svm.SVC(kernel='rbf')
        clf.fit(features2,sizeInt)
       
        X = np.array(features2) 
        y= np.array(sizeInt)

        X0, X1 = X[:, 0], X[:, 1]

        xx, yy = make_meshgrid(X0, X1)

    model.fit(features,size)
    
    #examples for trials
    ex_features = [[175,107,86,107],[170,91,76,102],[168,91,74,97],[168,81,69,99],[175,94,76,102],[170,109,94,117],[163,91,71,91],[163,86,69,97],[160,81,64,89],[168,114,102,127],[165,97,71,102],[165,99,76,97]]
    ex_label = ['Large (L)', 'Medium (M)', 'Small (S)', 'Small (S)', 'Medium (M)', 'Large (L)', 'Medium (M)', 'Small (S)', 'Small (S)', 'Large (L)', 'Medium (M)', 'Medium (M)']
    
    global i
    data = ex_features[i]
    
    #get prediction
    predicted = model.predict([data])[0]

    countS = 0
    countM = 0
    countL = 0
    bustNeighborS=[]
    bustNeighborM=[]
    bustNeighborL=[]
    hipsNeighborS=[]
    hipsNeighborM=[]
    hipsNeighborL=[]

    if trial.ai_method.name == "Nächste-Nachbarn-Klassifikation":
        neighbors = model.kneighbors([data], 25, False)
        for k in neighbors[0]:
            if size[k] == "Small (S)":
                countS += 1 
            elif size[k] == "Medium (M)":
                countM += 1
            else:
                countL += 1
                
        
        neighborsImage = clf.kneighbors([[data[1],data[3]]],25,False)
        if trial.context.name == "Immobilienpreis":
             for k in neighborsImage[0]:
                if size[k] == "Small (S)":
                    bustNeighborS.append(int((bust[k]-22)**1.14))
                    hipsNeighborS.append(int(hips[k]/10)-5)
                elif size[k] == "Medium (M)":
                    bustNeighborM.append(int((bust[k]-22)**1.14))
                    hipsNeighborM.append(int(hips[k]/10)-5) 
                else:
                    bustNeighborL.append(int((bust[k]-22)**1.14))
                    hipsNeighborL.append(int(hips[k]/10)-5)
        else:
     
             for k in neighborsImage[0]:
                if size[k] == "Small (S)":
                    bustNeighborS.append(bust[k])
                    hipsNeighborS.append(hips[k])
                elif size[k] == "Medium (M)":
                    bustNeighborM.append(bust[k])
                    hipsNeighborM.append(hips[k]) 
                else:
                    bustNeighborL.append(bust[k])
                    hipsNeighborL.append(hips[k])


    #plot data
    bustArrayS = []
    bustArrayM = []
    bustArrayL =[]
    hipsArrayS=[]
    hipsArrayM=[]
    hipsArrayL=[]

    l = 0

    if trial.context.name == "Immobilienpreis":
        while l < len(size):
            if size[l] == "Small (S)":
                bustArrayS.append(int((bust[l]-22)**1.14))
                hipsArrayS.append(int(hips[l]/10)-5)                  
            elif size[l] == "Medium (M)":
                bustArrayM.append(int((bust[l]-22)**1.14))
                hipsArrayM.append(int(hips[l]/10)-5)
            else:
                bustArrayL.append(int((bust[l]-22)**1.14))
                hipsArrayL.append(int(hips[l]/10)-5)
            l += 1
    else:
        while l < len(size):
            if size[l] == "Small (S)":
                bustArrayS.append(bust[l])
                hipsArrayS.append(hips[l])
            elif size[l] == "Medium (M)":
                bustArrayM.append(bust[l])
                hipsArrayM.append(hips[l])
            else:
                bustArrayL.append(bust[l])
                hipsArrayL.append(hips[l])
            l += 1

    plt.ion()

    if trial.context.name == "Immobilienpreis":
        if trial.ai_method.name == "Support-Vektor-Maschine":
            plt.plot(bustArrayS, hipsArrayS, 'rebeccapurple', marker= 5, markersize=7, linestyle = '')
            plt.plot(int((data[1]-22)**1.14), int(data[3]/10)-5, 'tab:red', marker = 6, markersize= 14,  linestyle = '', zorder=10)
            plt.plot(bustArrayM, hipsArrayM, 'darkgoldenrod', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'steelblue', marker = 4, markersize=7, linestyle = '')
        else:
            plt.plot(bustArrayS, hipsArrayS, '#d1bae8', marker= 5, markersize=7, linestyle = '')
            plt.plot(int((data[1]-22)**1.14), int(data[3]/10)-5, 'tab:red', marker = 6, markersize= 14,  linestyle = '', zorder=10)
            plt.plot(bustArrayM, hipsArrayM, '#edd498', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'lightsteelblue', marker = 4, markersize=7, linestyle = '')
            plt.plot(bustNeighborS, hipsNeighborS, 'rebeccapurple', marker= 5, markersize=10, linestyle = '')
            plt.plot(bustNeighborM, hipsNeighborM, 'darkgoldenrod', marker= 7, markersize=10, linestyle = '')
            plt.plot(bustNeighborL, hipsNeighborL, 'steelblue', marker = 4, markersize=10, linestyle = '')


        plt.xlim(80,199.99)
        plt.ylim(1.5,8.6)

        plt.xlabel('Grundstücksfläche [m²]', fontsize=14, labelpad=18, color='dimgrey')
        plt.ylabel('Zimmeranzahl', fontsize=14, labelpad=18, color='dimgrey')

        l=plt.legend(['< 400.000 €', 'Gegeben', '400.000 - 700.000 €', '> 700.000 €'],  bbox_to_anchor=(1.05, 1.15), loc='center right', framealpha=0, ncol=3, fontsize=12, columnspacing=1.5)

        l.legendHandles[1]._legmarker.set_markersize(7)
        l.legendHandles[0]._legmarker.set_color('rebeccapurple')
        l.legendHandles[2]._legmarker.set_color('darkgoldenrod')
        l.legendHandles[3]._legmarker.set_color('steelblue')

        texts=l.get_texts()
        texts[0].set_color("rebeccapurple")
        texts[2].set_color("darkgoldenrod")
        texts[3].set_color("steelblue")
        texts[1].set_color("tab:red")
    else:
        if trial.ai_method.name == "Support-Vektor-Maschine":
            plt.plot(bustArrayS, hipsArrayS, 'rebeccapurple', marker= 5, markersize=7, linestyle = '')
            plt.plot(bustArrayM, hipsArrayM, 'darkgoldenrod', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'steelblue', marker = 4, markersize=7, linestyle = '')
            plt.plot(data[1], data[3], 'tab:red', marker = 6, markersize= 14,  linestyle = '', zorder=10)
        else:
            plt.plot(bustArrayS, hipsArrayS, '#d1bae8', marker= 5, markersize=7, linestyle = '')
            plt.plot(bustArrayM, hipsArrayM, '#edd498', marker= 7, markersize=7, linestyle = '')
            plt.plot(bustArrayL, hipsArrayL, 'lightsteelblue', marker = 4, markersize=7, linestyle = '')
            plt.plot(data[1], data[3], 'tab:red', marker = 6, markersize= 14,  linestyle = '', zorder=10)
            plt.plot(bustNeighborS, hipsNeighborS, 'rebeccapurple', marker= 5, markersize=10, linestyle = '')
            plt.plot(bustNeighborM, hipsNeighborM, 'darkgoldenrod', marker= 7, markersize=10, linestyle = '')
            plt.plot(bustNeighborL, hipsNeighborL, 'steelblue', marker = 4, markersize=10, linestyle = '')
        
        plt.xlim(70,126.5)
        plt.ylim(70,136)
    
        plt.xlabel('Brustumfang [cm]', fontsize=14, labelpad=18, color='dimgrey')
        plt.ylabel('Hüftumfang [cm]', fontsize=14, labelpad=18, color='dimgrey')

        l=plt.legend(['Small (S)', 'Medium (M)', 'Large (L)', 'Gegeben'],  bbox_to_anchor=(1.05, 1.15), loc='center right', framealpha=0, ncol=4, fontsize=12, columnspacing=1.5)
    
        l.legendHandles[3]._legmarker.set_markersize(7)
        l.legendHandles[0]._legmarker.set_color('rebeccapurple')
        l.legendHandles[1]._legmarker.set_color('darkgoldenrod')
        l.legendHandles[2]._legmarker.set_color('steelblue')
        texts=l.get_texts()
        texts[0].set_color("rebeccapurple")
        texts[1].set_color("darkgoldenrod")
        texts[2].set_color("steelblue")
        texts[3].set_color("tab:red")


    plt.gcf().subplots_adjust(bottom=0.15)
    plt.gcf().subplots_adjust(left=0.15)
    plt.gcf().subplots_adjust(top=0.85)

    for ax in plt.gcf().axes:
        ax.spines['bottom'].set_color('grey')
        ax.spines['left'].set_color('grey')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(axis='x', colors='dimgrey')
        ax.tick_params(axis='y', colors='dimgrey')
        
        if trial.context.name == "Immobilienpreis":            
            ax.plot((1), (1.5), ls="", marker=">", ms=10, color="dimgrey", transform=ax.get_yaxis_transform(), clip_on=False)
            ax.plot((80), (1), ls="", marker="^", ms=10, color="dimgrey", transform=ax.get_xaxis_transform(), clip_on=False)

        else:
            ax.plot((1), (70), ls="", marker=">", ms=10, color="dimgrey", transform=ax.get_yaxis_transform(), clip_on=False)
            ax.plot((70), (1), ls="", marker="^", ms=10, color="dimgrey", transform=ax.get_xaxis_transform(), clip_on=False)
        
        if trial.ai_method.name == "Support-Vektor-Maschine":
            plot_contours(ax, clf, xx, yy,colors=['rebeccapurple', 'dimgrey','dimgrey','darkgoldenrod', 'dimgrey','dimgrey','dimgrey','steelblue'], alpha=0.3)

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
        
    plt.savefig('surveys/static/surveys/img/visuell.png', transparent=True)

    plt.show()
    plt.close()
   
    label = ex_label[i]

    #convert data for context "house prices"
    if trial.context.name == "Immobilienpreis":
        data[0] = data[0]*3+1465                #range: 1900-2020
        data[1] = int((data[1]-22)**1.14)       #range: 90-234
        data[2] = int((data[2]-17)**1.1)        #range: 56-176
        data[3] = int(data[3]/10)-5             #range: 2-10
        if predicted == "Small (S)":
            predicted = "< 400.000 €"
        elif predicted == "Medium (M)":
            predicted = "400.000 - 700.000 €"
        else: 
            predicted = "> 700.000 €"
        if label == "Small (S)":
            label = "< 400.000 €"
        elif label == "Medium (M)":
            label = "400.000 - 700.000 €"
        else:
            label = "> 700.000 €"
   
    # creates new database trial
    db_trial = Trial(sessionkey=session, blockcounter=block.blockcounter, context=trial.context.name, ai_method=trial.ai_method.name, explanation_approach=trial.explanation_approach.name, ai_recommendation=predicted, label=label)
    db_trial.save()  

    context = {
        'set':set,
        'session': session,
        'survey': survey,
        'blockcounter': block.blockcounter,
        'trial': db_trial,
        'language': language,
        'max': block.max,
        'trial': trial,
        'db_trial': db_trial,
        'data0': data[0],
        'data1': data[1],
        'data2': data[2],
        'data3': data[3],
        'predicted': predicted,
        'countS': countS,
        'countM': countM,
        'countL': countL
    }

    return render(request, 'surveys/trial.html', context )

# Saves trial
def save_trial(request, session_key, survey_id, trial_id):
    
    global i
    i = i+1

    survey = get_object_or_404(Survey, id = survey_id)
    session = get_object_or_404(Session, key=session_key)

    # If session key is not current users session key, raise error
    if session.key != request.session.session_key:
        error_message = "Wrong session key"
        return render(request, 'surveys/error.html', {'error_message': error_message, 'session':session, 'survey':survey})

    #gets trial
    trial = get_object_or_404(Trial, id=trial_id)
    if request.method == 'POST':
        trial.choice = request.POST.get('auswahl');
        trial.rating_1 = request.POST.get('bewertung_1');
        trial.rating_2 = request.POST.get('bewertung_2');
        trial.rating_3 = request.POST.get('bewertung_3');
        trial.rating_4 = request.POST.get('bewertung_4');
        trial.rating_5 = request.POST.get('bewertung_5');
        trial.decision = request.POST.get('entscheidung');
    trial.save()

    # Loads saved session set
    try:
        with open('sessions/set_'+ session_key, 'rb') as f:
            set = pickle.load(f)
    except:
        return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    # Pops the highest trial
    if not set.top().isEmpty():
        set.top().pop()

        #Save set to pickle
        try:
            with open('sessions/set_'+session_key, 'wb') as f:
                pickle.dump(set, f)
        except:
            return render(request, 'surveys/error.html', {'error_message':'Session not found, sorry', 'survey': survey})

    return redirect('surveys:trial', survey_id, session_key)

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
