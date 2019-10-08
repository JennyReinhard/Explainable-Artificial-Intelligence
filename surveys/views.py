from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Session, Redirect
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SurveyUpdateForm, SurveyCreateFrom
from django.forms import inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied


# Generic survey view displaying a list of all surveys
class SurveysView(LoginRequiredMixin,generic.ListView):
    model = Survey

# Generic detail View for a Surveys
class SurveyDetailView(LoginRequiredMixin,generic.DetailView):
    model = Survey

# Generic create view to create a new survey
def create_survey(request):
    if request.method == 'POST':
        form = SurveyCreateFrom(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
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


# Generic update view to edit a survey
def edit_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    RedirectFormset = inlineformset_factory(Survey, Redirect, fields=('purpose', 'url'), extra=3, max_num=3)

    if survey.user is not request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = SurveyUpdateForm(request.POST or None, instance=survey)
        formset = RedirectFormset(request.POST or None, instance=survey)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Survey was edited successfully')
            return redirect('surveys:survey', pk=survey.id)
        else:
            messages.error(request, formset.errors)
            return redirect('surveys:edit-survey', pk=survey.id)

    else:
        form = SurveyUpdateForm(instance=survey)
        formset = RedirectFormset(instance=survey)
        context = {
            'form': form,
            'formset': formset,
            'survey': survey
        }

    return render(request, 'surveys/edit_survey.html', context)

# View function that deletes a survey
def delete_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Survey successfully deleted')
        return redirect('surveys:surveys')

def start_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    try:
        redirect = survey.redirect_set.get(purpose=0)
    except ObjectDoesNotExist:
        redirect = None

    request.session.flush()
    request.session.create()
    session_key = request.session.session_key
    client_ip = '127.0.0.1'
    session = Session(survey=survey, key=session_key, ip_address=client_ip)
    session.save()

    context = {
        'survey': survey,
        'session': session,
        'redirect': redirect
    }

    return render(request, 'surveys/start_survey.html', context)

#404 handler
def handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)

#500 handler
def handler500(request, *args, **kwargs):
    return render(request, '500.html', status=500)
