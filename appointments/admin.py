"""
Django Admin configuration for the healthcare application.

These classes control how patients, appointments, and neighbourhoods
are displayed and searched in the Django Admin site.
"""

from django.contrib import admin
from .models import Patient, Appointment, Neighbourhood


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    # Show the most useful patient details in the admin list.
    list_display = ('patient_id', 'gender', 'age', 'diabetes', 'hypertension')

    # Allow staff to quickly filter patients by common health fields.
    list_filter = ('gender', 'diabetes', 'hypertension')

    # Let staff search for a patient using the dataset patient ID.
    search_fields = ('patient_id',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Show the main appointment details in the admin list.
    list_display = ('appointment_id', 'patient', 'showed_up', 'sms_received', 'scheduled_day')

    # Make it easier to review attendance and SMS reminder records.
    list_filter = ('showed_up', 'sms_received')

    # Allow appointments to be found using their appointment ID.
    search_fields = ('appointment_id',)


@admin.register(Neighbourhood)
class NeighbourhoodAdmin(admin.ModelAdmin):
    # Allow neighbourhoods to be searched by name.
    search_fields = ('name',)