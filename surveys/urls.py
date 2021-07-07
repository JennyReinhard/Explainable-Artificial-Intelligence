from django.urls import path
from surveys.views import SurveysView, SurveyUptateView
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'surveys'

urlpatterns = [
    path('', SurveysView.as_view(), name='surveys'),
    path('<int:pk>/', views.survey_detail, name='survey'),
    path('new/', login_required(views.create_survey), name='create-survey'),
    path('<int:pk>/delete/', login_required(views.delete_survey), name='delete-survey'),
    path('<int:pk>/edit/', login_required(SurveyUptateView.as_view()), name='edit-survey'),
    path('<int:pk>/delete-sessions/', login_required(views.delete_sessions), name='delete-sessions'),

    path('<int:pk>/introduction/', views.introduction, name='introduction'),
    path('<int:survey_id>/load/', views.load_set, name='load-survey'),
    path('<int:survey_id>/<slug:session_key>/', views.session_detail, name='session'),
    path('<int:survey_id>/<slug:session_key>/instructions/', views.instructions, name='instructions'),
    path('<int:survey_id>/<slug:session_key>/instructions2/', views.instructions2, name='instructions2'),
    path('<int:survey_id>/<slug:session_key>/testround/', views.testround, name='testround'),
    path('<int:survey_id>/<slug:session_key>/testround_end/', views.testround_end, name='testround_end'),

    path('<int:survey_id>/<slug:session_key>/survey/ready/', views.survey_ready, name='survey-ready'),
    path('<int:survey_id>/<slug:session_key>/block/ready/', views.block_ready, name='block-ready'),

    path('<int:survey_id>/<slug:session_key>/trial/', views.trial, name='trial'),
    path('<int:survey_id>/<slug:session_key>/trial/save/<int:trial_id>/', views.save_trial, name='save-trial'),

    path('<int:survey_id>/<slug:session_key>/training/', views.training, name='training'),
    path('<int:survey_id>/<slug:session_key>/save-training/', views.save_training, name='save-training'),

    path('<int:survey_id>/<slug:session_key>/end/', views.end, name='end'),

]
