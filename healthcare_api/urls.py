"""
Main URL configuration for the Healthcare Appointment API.

This file connects the main pages of the application,
including the homepage, patient form, Django Admin,
and the REST API endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from appointments.views import home, patient_form

urlpatterns = [
    # Homepage
    path('', home, name='home'),

    # HTML form to add a new patient
    path('patients/add/', patient_form, name='patient_form'),

    # Django Admin page
    path('admin/', admin.site.urls),

    # REST API routes for the application
    path('api/', include('appointments.urls')),
]