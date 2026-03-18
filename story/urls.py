from django.urls import path

from .views import opening_story_view

urlpatterns = [
    path('opening/', opening_story_view, name='opening_story'),
]
