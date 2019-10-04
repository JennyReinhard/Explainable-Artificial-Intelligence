from django.shortcuts import render, redirect, get_object_or_404
from . import views
from .forms import PostForm
from .models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

# Renders the homepage
def home(request):
    homepage = get_object_or_404(Post, type='HOMEPAGE')
    context = {
        'homepage': homepage
    }
    return render(request, 'home/index.html', context)

#Creates a new post
@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post successfully created.')
            return redirect('home:index')
    else:
        form=PostForm()
        context = {
            'form': form
        }
    return render(request, 'home/new-post.html', context)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post successfully updated')
            return redirect('home:index')
        else:
            messages.error(request, form.errors)
            return redirect('home:edit-post', post_id=post.id)

    else:
        form = PostForm(instance=post)
        context = {
            'form': form
        }

    return render(request, 'home/edit-post.html', context)
