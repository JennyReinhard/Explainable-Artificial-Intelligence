from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from surveys.models import Survey, Trial, Session
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg,Sum
import io
import os
from framework.settings import BASE_DIR
# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Create your views here.
class Sessions(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, session_key):

        session = get_object_or_404(Session, key=session_key)
        trials = [trial.id for trial in Trial.objects.filter(sessionkey=session)]

        data = {
            'session': session,
            'trials': trials
        }
        return Response(data)

class Surveys(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, pk=survey_id)
        trials = Trial.objects.filter(sessionkey__survey=survey)

        data = {
            'survey': survey,
            'trials': trials
        }

        return Response(data)
