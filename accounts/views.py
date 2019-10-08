from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import login, authenticate
# Create your views here.

# Sign up view that creates new user and logs user in
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Your account has been successfully created and you are logged in with {}.'.format(username))
            return redirect('home:index')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
