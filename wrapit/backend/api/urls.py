from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
    path('top_tracks/', views.top_tracks, name='top_tracks'),
    path('top_artists/', views.top_artists, name='top_artists')
]