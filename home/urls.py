from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


app_name = 'home'

urlpatterns = [
    #path('', views.home, name='index'),
    #path('post/new/', login_required(views.PostCreateView.as_view()), name='new-post'),
    #path('post/<int:pk>/update/', login_required(views.PostUpdateView.as_view()), name="update-post")
]
