from django.urls import path

from .views import level_config_api, level_view, submit_decision_api

urlpatterns = [
    path('<int:level_order>/', level_view, name='level'),
    path('<int:level_order>/config/', level_config_api, name='level_config_api'),
    path('<int:level_order>/submit/', submit_decision_api, name='submit_decision_api'),
]
