from django.shortcuts import render
from . import views
# Create your views here.

# Renders the homepage
def home(request):
    context = {
        'title': 'Risky Wally Homepage'
    }
    return render(request, 'home/index.html', context)
