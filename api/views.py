from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from surveys.models import Survey, Trial, Session
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg,Sum
import io
import os
from riskywally.settings import BASE_DIR
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

def transcribe(request, session_key):

    session = get_object_or_404(Session, key=session_key)

    # Instantiates a client
    client = speech.SpeechClient()


    file_name = BASE_DIR+session.audio.url


    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=48000,
        language_code='de-DE')

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    transcript = ""

    for result in response.results:
        transcript += result.alternatives[0].transcript

    session.transcript = transcript
    session.save()


    return redirect('surveys:session', survey_id=session.survey.id, session_key=session.key)
