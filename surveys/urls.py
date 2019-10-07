from django.urls import path
from surveys.views import SurveysView, SurveyDetailView, SurveyCreateView, SurveyDeleteView, SurveyUpdateView
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'surveys'

urlpatterns = [
    path('',login_required(SurveysView.as_view()), name='surveys'),
    path('<int:pk>/', login_required(SurveyDetailView.as_view()), name='survey'),
    path('new/', login_required(SurveyCreateView.as_view()), name='create-survey'),
    path('<int:pk>', login_required(SurveyUpdateView.as_view()),name='update-survey'),
    path('<int:pk>/delete/', views.delete_survey, name='delete-survey')

]
