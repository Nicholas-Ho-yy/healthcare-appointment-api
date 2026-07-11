from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import PatientForm
from .models import Appointment, Neighbourhood, Patient
from .serializers import (
    AppointmentSerializer,
    NeighbourhoodSerializer,
    PatientSerializer,
)


DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


def parse_integer_parameter(request, name, minimum=None, maximum=None):
    """
    Read an optional number from the query string.

    If the value is missing, return None. If it is invalid,
    return a clear 400 Bad Request response.
    """
    raw_value = request.query_params.get(name)

    if raw_value in (None, ""):
        return None, None

    try:
        value = int(raw_value)
    except ValueError:
        return None, Response(
            {"error": f"'{name}' must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if minimum is not None and value < minimum:
        return None, Response(
            {"error": f"'{name}' must be at least {minimum}."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if maximum is not None and value > maximum:
        return None, Response(
            {"error": f"'{name}' must not exceed {maximum}."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return value, None


def parse_boolean_parameter(request, name):
    """
    Read an optional true or false value from the query string.

    The API also accepts 1/0 and yes/no to make the
    parameter easier to use.
    """

    raw_value = request.query_params.get(name)

    if raw_value in (None, ""):
        return None, None

    normalised_value = raw_value.strip().lower()

    if normalised_value in {"true", "1", "yes"}:
        return True, None

    if normalised_value in {"false", "0", "no"}:
        return False, None

    return None, Response(
        {
            "error": (
                f"'{name}' must be true or false "
                "(1/0 and yes/no are also accepted)."
            )
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def get_limit(request):
    """
    Read and check the requested result limit.

    The API returns 100 records by default and allows
    callers to request up to 1,000 records.
    """

    raw_limit = request.query_params.get("limit")

    if raw_limit in (None, ""):
        return DEFAULT_LIMIT, None

    limit, error_response = parse_integer_parameter(
        request,
        "limit",
        minimum=1,
        maximum=MAX_LIMIT,
    )

    return limit, error_response


def home(request):
    """Show the homepage and links to the API examples."""

    return render(request, "appointments/home.html")


def patient_form(request):
    """Show the patient form and save valid submissions."""

    if request.method == "POST":
        form = PatientForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = PatientForm()

    return render(
        request,
        "appointments/patient_form.html",
        {"form": form},
    )


@api_view(["GET", "POST"])
def patient_list(request):
    """
    Return patient records or create a new patient.

    The GET parameters below can be used separately
    or combined to produce different patient queries.

    Supported GET parameters:
        min_age
        max_age
        gender
        diabetes
        hypertension
        scholarship
        limit

    Examples:
        /api/patients/?min_age=40&max_age=60
        /api/patients/?diabetes=true
        /api/patients/?min_age=65&diabetes=true&hypertension=true
        /api/patients/?limit=20
    """

    if request.method == "POST":
        # Validate and save a new patient sent through the API.
        serializer = PatientSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    patients = Patient.objects.all()

    min_age, error_response = parse_integer_parameter(
        request,
        "min_age",
        minimum=0,
        maximum=120,
    )
    if error_response:
        return error_response

    max_age, error_response = parse_integer_parameter(
        request,
        "max_age",
        minimum=0,
        maximum=120,
    )
    if error_response:
        return error_response

    if min_age is not None and max_age is not None and min_age > max_age:
        return Response(
            {"error": "'min_age' cannot be greater than 'max_age'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    diabetes, error_response = parse_boolean_parameter(
        request,
        "diabetes",
    )
    if error_response:
        return error_response

    hypertension, error_response = parse_boolean_parameter(
        request,
        "hypertension",
    )
    if error_response:
        return error_response

    scholarship, error_response = parse_boolean_parameter(
        request,
        "scholarship",
    )
    if error_response:
        return error_response

    limit, error_response = get_limit(request)
    if error_response:
        return error_response

    gender = request.query_params.get("gender")

    if min_age is not None:
        patients = patients.filter(age__gte=min_age)

    if max_age is not None:
        patients = patients.filter(age__lte=max_age)

    if gender:
        gender = gender.strip().upper()

        if gender not in {"M", "F"}:
            return Response(
                {"error": "'gender' must be M or F."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        patients = patients.filter(gender=gender)

    if diabetes is not None:
        patients = patients.filter(diabetes=diabetes)

    if hypertension is not None:
        patients = patients.filter(hypertension=hypertension)

    if scholarship is not None:
        patients = patients.filter(scholarship=scholarship)

    serializer = PatientSerializer(
        patients[:limit],
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def patient_detail(request, pk):
    """
    Retrieve, replace, partially update or delete one patient.
    """

    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "GET":
        serializer = PatientSerializer(
            patient,
            context={"request": request},
        )
        return Response(serializer.data)

    if request.method in {"PUT", "PATCH"}:
        serializer = PatientSerializer(
            patient,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    patient.delete()

    return Response(
        {"message": "Patient deleted successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
def appointment_list(request):
    """
    Return appointment records or create a new appointment.

    The GET parameters can be combined to perform more
    advanced searches across appointments, patients,
    and neighbourhoods.

    Supported GET parameters:
        showed_up
        sms_received
        min_age
        max_age
        diabetes
        hypertension
        neighbourhood
        min_wait_days
        max_wait_days
        limit

    Examples:
        /api/appointments/?showed_up=false
        /api/appointments/?showed_up=false&sms_received=true
        /api/appointments/?min_age=40&max_age=60
        /api/appointments/?min_wait_days=30
        /api/appointments/?neighbourhood=JARDIM
    """

    if request.method == "POST":
        # Validate and save a new appointment sent through the API.
        serializer = AppointmentSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Load the related patient and neighbourhood in the same query
    # so Django does not need extra database lookups for every record.
    appointments = Appointment.objects.select_related(
        "patient",
        "neighbourhood",
    ).all()

    min_age, error_response = parse_integer_parameter(
        request,
        "min_age",
        minimum=0,
        maximum=120,
    )
    if error_response:
        return error_response

    max_age, error_response = parse_integer_parameter(
        request,
        "max_age",
        minimum=0,
        maximum=120,
    )
    if error_response:
        return error_response

    if min_age is not None and max_age is not None and min_age > max_age:
        return Response(
            {"error": "'min_age' cannot be greater than 'max_age'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    min_wait_days, error_response = parse_integer_parameter(
        request,
        "min_wait_days",
    )
    if error_response:
        return error_response

    max_wait_days, error_response = parse_integer_parameter(
        request,
        "max_wait_days",
    )
    if error_response:
        return error_response

    if (
        min_wait_days is not None
        and max_wait_days is not None
        and min_wait_days > max_wait_days
    ):
        return Response(
            {
                "error": (
                    "'min_wait_days' cannot be greater than "
                    "'max_wait_days'."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    showed_up, error_response = parse_boolean_parameter(
        request,
        "showed_up",
    )
    if error_response:
        return error_response

    sms_received, error_response = parse_boolean_parameter(
        request,
        "sms_received",
    )
    if error_response:
        return error_response

    diabetes, error_response = parse_boolean_parameter(
        request,
        "diabetes",
    )
    if error_response:
        return error_response

    hypertension, error_response = parse_boolean_parameter(
        request,
        "hypertension",
    )
    if error_response:
        return error_response

    limit, error_response = get_limit(request)
    if error_response:
        return error_response

    neighbourhood = request.query_params.get("neighbourhood")

    if showed_up is not None:
        appointments = appointments.filter(showed_up=showed_up)

    if sms_received is not None:
        appointments = appointments.filter(sms_received=sms_received)

    if min_age is not None:
        appointments = appointments.filter(patient__age__gte=min_age)

    if max_age is not None:
        appointments = appointments.filter(patient__age__lte=max_age)

    if diabetes is not None:
        appointments = appointments.filter(patient__diabetes=diabetes)

    if hypertension is not None:
        appointments = appointments.filter(
            patient__hypertension=hypertension
        )

    if neighbourhood:
        appointments = appointments.filter(
            neighbourhood__name__icontains=neighbourhood.strip()
        )

    if min_wait_days is not None:
        appointments = appointments.filter(
            date_difference__gte=min_wait_days
        )

    if max_wait_days is not None:
        appointments = appointments.filter(
            date_difference__lte=max_wait_days
        )

    serializer = AppointmentSerializer(
        appointments[:limit],
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def appointment_detail(request, pk):
    """Retrieve, update or delete one appointment."""

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient",
            "neighbourhood",
        ),
        pk=pk,
    )

    if request.method == "GET":
        serializer = AppointmentSerializer(
            appointment,
            context={"request": request},
        )
        return Response(serializer.data)

    if request.method in {"PUT", "PATCH"}:
        serializer = AppointmentSerializer(
            appointment,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    appointment.delete()

    return Response(
        {"message": "Appointment deleted successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def neighbourhood_list(request):
    """
    Return neighbourhood records.

    The optional search parameter matches part of a
    neighbourhood name, while limit controls the result count.
    """

    neighbourhoods = Neighbourhood.objects.all()

    search = request.query_params.get("search")

    limit, error_response = get_limit(request)
    if error_response:
        return error_response

    if search:
        neighbourhoods = neighbourhoods.filter(
            name__icontains=search.strip()
        )

    serializer = NeighbourhoodSerializer(
        neighbourhoods[:limit],
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["GET"])
def neighbourhood_detail(request, pk):
    """Return one neighbourhood."""

    neighbourhood = get_object_or_404(Neighbourhood, pk=pk)

    serializer = NeighbourhoodSerializer(
        neighbourhood,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["GET"])
def no_show_rate(request):
    """
    Calculate the overall attendance and no-show statistics.
    """

    total_appointments = Appointment.objects.count()
    no_show_count = Appointment.objects.filter(showed_up=False).count()
    showed_up_count = Appointment.objects.filter(showed_up=True).count()

    if total_appointments == 0:
        no_show_rate_percent = 0
    else:
        no_show_rate_percent = round(
            (no_show_count / total_appointments) * 100,
            2,
        )

    return Response(
        {
            "total_appointments": total_appointments,
            "showed_up_count": showed_up_count,
            "no_show_count": no_show_count,
            "no_show_rate_percent": no_show_rate_percent,
        }
    )