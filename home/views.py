from django.shortcuts import render, redirect, get_object_or_404
from . import views
from .models import Post, Setting
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.

# Renders the homepage
def home(request):
    homepage = get_object_or_404(Post, type='HOMEPAGE')
    active_survey = 1
    try:
        active_survey = get_object_or_404(Setting, name="Active Survey")
        active_survey = active_survey.value
    except:
        print("Active Survey not set!")
    context = {
        'homepage': homepage,
        'active_survey': active_survey
    }
    return render(request, 'home/index.html', context)

# Generic view for creating a post
class PostCreateView(SuccessMessageMixin, generic.CreateView):
    model = Post
    fields = [
        'title',
        'content',
        'type'
    ]
    success_message = "Post was created successfully"

# Generic view for update a post
class PostUpdateView(SuccessMessageMixin, generic.UpdateView):
    model = Post
    fields = [
        'title',
        'content',
        'type'
    ]

    success_message = "Post was updated successfully"
