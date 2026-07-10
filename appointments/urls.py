from django.urls import path
from . import views

urlpatterns = [

    # Homepage
    path("", views.home, name="home"),

    # HTML Form
    path("patient-form/", views.patient_form, name="patient_form"),

    # Patient endpoints
    path(
        "patients/",
        views.patient_list,
        name="patient-list"
    ),
    path(
        "patients/<int:pk>/",
        views.patient_detail,
        name="patient-detail"
    ),

    # Appointment endpoints
    path(
        "appointments/",
        views.appointment_list,
        name="appointment-list"
    ),
    path(
        "appointments/<int:pk>/",
        views.appointment_detail,
        name="appointment-detail"
    ),

    # Neighbourhood endpoints
    path(
        "neighbourhoods/",
        views.neighbourhood_list,
        name="neighbourhood-list"
    ),
    path(
        "neighbourhoods/<int:pk>/",
        views.neighbourhood_detail,
        name="neighbourhood-detail"
    ),

    # Statistics endpoint
    path(
        "statistics/no-show-rate/",
        views.no_show_rate,
        name="no-show-rate"
    ),
]