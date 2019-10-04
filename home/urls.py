from django.urls import path
from . import views
app_name = 'home'

urlpatterns = [
    path('', views.home, name='index'),
    path('newpost/', views.new_post, name='new-post'),
    path('editpost/<int:post_id>/', views.edit_post, name='edit-post')
]
