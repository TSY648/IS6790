from django.urls import path

from .views import level_story_view, opening_story_view

urlpatterns = [
    path('opening/', opening_story_view, name='opening_story'),
    path('level/<int:level_order>/', level_story_view, name='level_story'),
]
