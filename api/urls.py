from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('sessions/<slug:session_key>/', views.Sessions.as_view(), name='api-sessions'),
    path('surveys/<int:survey_id>/', views.Surveys.as_view(), name='api-surveys'),
]
