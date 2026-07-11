from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Patient, Neighbourhood, Appointment


class APITest(TestCase):
    """
    Tests the main API endpoints, filters, validation rules,
    and CRUD operations used by the application.
    """

    def setUp(self):
         # Create a fresh API client before each test.
        self.client = APIClient()

        # This patient matches the high-risk filters used
        # in several of the appointment tests.
        self.patient = Patient.objects.create(
            patient_id="TEST001",
            gender="M",
            age=70,
            scholarship=False,
            hypertension=True,
            diabetes=True,
            alcoholism=False,
            handicap=0
        )

        self.neighbourhood = Neighbourhood.objects.create(
            name="TEST_NEIGHBOURHOOD"
        )

        # Create one missed appointment that received an SMS reminder.
        self.appointment = Appointment.objects.create(
            appointment_id="APP001",
            patient=self.patient,
            neighbourhood=self.neighbourhood,
            scheduled_day=timezone.now(),
            appointment_day=timezone.now() + timezone.timedelta(days=3),
            sms_received=True,
            showed_up=False,
            date_difference=3
        )

    # Check that the main pages and resource endpoints are available.
    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_list_endpoint(self):
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_appointment_list_endpoint(self):
        response = self.client.get("/api/appointments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_neighbourhood_list_endpoint(self):
        response = self.client.get("/api/neighbourhoods/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_patient_detail_endpoint(self):
        response = self.client.get(f"/api/patients/{self.patient.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["patient_id"], "TEST001")

    def test_appointment_detail_endpoint(self):
        response = self.client.get(f"/api/appointments/{self.appointment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["appointment_id"], "APP001")

    # Check that query parameters return the expected records.
    def test_filter_patients_by_min_age(self):
        response = self.client.get("/api/patients/?min_age=65")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_patients_by_diabetes(self):
        response = self.client.get("/api/patients/?diabetes=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_appointments_by_no_show(self):
        response = self.client.get("/api/appointments/?showed_up=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_sms_no_shows(self):
        response = self.client.get(
            "/api/appointments/?showed_up=false&sms_received=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_high_risk_no_shows(self):
        response = self.client.get(
            "/api/appointments/?showed_up=false&min_age=65&diabetes=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Check the summary values returned by the statistics endpoint.
    def test_no_show_rate_endpoint(self):
        response = self.client.get("/api/statistics/no-show-rate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_appointments"], 1)
        self.assertEqual(response.data["no_show_count"], 1)
        self.assertEqual(response.data["showed_up_count"], 0)

    # Check patient creation, validation, updating, and deletion.
    def test_create_patient(self):
        data = {
            "patient_id": "TEST002",
            "gender": "F",
            "age": 25,
            "scholarship": False,
            "hypertension": False,
            "diabetes": False,
            "alcoholism": False,
            "handicap": 0
        }

        response = self.client.post("/api/patients/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)

    def test_invalid_age_validation(self):
        data = {
            "patient_id": "TEST003",
            "gender": "M",
            "age": -5,
            "scholarship": False,
            "hypertension": False,
            "diabetes": False,
            "alcoholism": False,
            "handicap": 0
        }

        response = self.client.post("/api/patients/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)

    def test_invalid_gender_validation(self):
        data = {
            "patient_id": "TEST004",
            "gender": "X",
            "age": 30,
            "scholarship": False,
            "hypertension": False,
            "diabetes": False,
            "alcoholism": False,
            "handicap": 0
        }

        response = self.client.post("/api/patients/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gender", response.data)

    def test_update_patient(self):
        response = self.client.patch(
            f"/api/patients/{self.patient.id}/",
            {"age": 71},
            format="json"
        )

        self.patient.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.patient.age, 71)

    def test_delete_patient(self):
        response = self.client.delete(f"/api/patients/{self.patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Patient.objects.count(), 0)

    # Check the cross-field validation in AppointmentSerializer.
    def test_invalid_appointment_date_order(self):
        data = {
            "appointment_id": "APP002",
            "patient": f"http://testserver/api/patients/{self.patient.id}/",
            "neighbourhood": f"http://testserver/api/neighbourhoods/{self.neighbourhood.id}/",
            "scheduled_day": timezone.now().isoformat(),
            "appointment_day": (
                timezone.now() - timezone.timedelta(days=5)
            ).isoformat(),
            "sms_received": False,
            "showed_up": False,
            "date_difference": -5
        }

        response = self.client.post("/api/appointments/", data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )