from django.urls import path

from .views import progress_ping

urlpatterns = [
    path('ping/', progress_ping, name='progress_ping'),
]
