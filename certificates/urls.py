from django.urls import path

from .views import certificate_summary_view, certificate_view

urlpatterns = [
    path('summary/', certificate_summary_view, name='certificate_summary'),
    path('', certificate_view, name='certificate'),
]
