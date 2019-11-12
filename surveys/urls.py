from django.urls import path
from surveys.views import SurveysView, SurveyUptateView
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'surveys'

urlpatterns = [
    path('', SurveysView.as_view(), name='surveys'),
    path('<int:survey_id>/', views.survey_detail, name='survey'),
    path('new/', login_required(views.create_survey), name='create-survey'),
    path('<int:pk>/delete/', login_required(views.delete_survey), name='delete-survey'),
    path('<int:pk>/edit/', login_required(SurveyUptateView.as_view()), name='edit-survey'),
    path('<int:pk>/delete-sessions/', login_required(views.delete_sessions), name='delete-sessions'),
    path('<int:survey_id>/introduction/', views.introduction, name='introduction'),
    path('<int:survey_id>/<slug:session_key>/instructions/', views.instructions, name='instructions'),
    path('<int:survey_id>/<slug:session_key>/trial/', views.trial, name='trial'),
    path('<int:survey_id>/load/', views.load_set, name='load-survey'),
    path('trial/save/<int:trial_id>/', views.save_trial, name='save-trial'),
    path('trial/save-feedback/<int:trial_id>/', views.save_feedback, name='save-feedback'),
    path('<int:survey_id>/<slug:session_key>/block/ready/', views.block_ready, name='block-ready'),
    path('<int:survey_id>/<slug:session_key>/training/', views.training, name='training'),
    path('<int:survey_id>/<slug:session_key>/save-training/', views.save_training, name='save-training'),
    path('<int:survey_id>/<slug:session_key>/survey/ready/', views.survey_ready, name='survey-ready'),
    path('<int:survey_id>/<slug:session_key>/end/', views.end, name='end'),

    path('<int:survey_id>/<slug:session_key>/', views.session_detail, name='session'),
    path('api/sessions/<slug:session_key>/', views.Sessions.as_view(), name='api-sessions'),
    path('api/surveys/<int:survey_id>/', views.Surveys.as_view(), name='api-surveys')



]
