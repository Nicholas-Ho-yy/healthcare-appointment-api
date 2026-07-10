from django.contrib import admin
from .models import Patient, Appointment, Neighbourhood


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'gender', 'age', 'diabetes', 'hypertension')
    list_filter = ('gender', 'diabetes', 'hypertension')
    search_fields = ('patient_id',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'patient', 'showed_up', 'sms_received', 'scheduled_day')
    list_filter = ('showed_up', 'sms_received')
    search_fields = ('appointment_id',)


@admin.register(Neighbourhood)
class NeighbourhoodAdmin(admin.ModelAdmin):
    search_fields = ('name',)