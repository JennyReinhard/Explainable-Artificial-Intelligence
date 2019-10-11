from django.urls import path
from surveys.views import SurveysView, SurveyDetailView, SurveyUptateView
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'surveys'

urlpatterns = [
    path('', SurveysView.as_view(), name='surveys'),
    path('<int:pk>/', SurveyDetailView.as_view(), name='survey'),
    path('new/', login_required(views.create_survey), name='create-survey'),
    path('<int:pk>/delete/', login_required(views.delete_survey), name='delete-survey'),
    path('<int:pk>/edit/', login_required(SurveyUptateView.as_view()), name='edit-survey'),
    path('<int:pk>/delete-sessions/', login_required(views.delete_sessions), name='delete-sessions'),
    path('<int:survey_id>/start/', views.start_survey, name='start-survey'),
    path('<int:survey_id>/<slug:session_key>/ready/', views.survey_ready, name='survey-ready')


]
