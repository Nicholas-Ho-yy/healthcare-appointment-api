from django.core.validators import MaxValueValidator
from django.db import models


class Patient(models.Model):
    """
    Stores one patient from the healthcare no-show dataset.
    Each patient can have many appointments.
    """

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    patient_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    age = models.PositiveSmallIntegerField(validators=[MaxValueValidator(120)])

    scholarship = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    alcoholism = models.BooleanField(default=False)

    # In the original dataset, Handicap can contain values above 1.
    handicap = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)]
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["age"]),
            models.Index(fields=["gender"]),
        ]

    def __str__(self):
        return f"Patient {self.patient_id}"


class Neighbourhood(models.Model):
    """
    Stores each unique neighbourhood only once.
    Appointments link to this table using a foreign key.
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Appointment(models.Model):
    """
    Stores appointment records and links each appointment
    to a patient and a neighbourhood.
    """

    appointment_id = models.CharField(max_length=50, unique=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    neighbourhood = models.ForeignKey(
        Neighbourhood,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    scheduled_day = models.DateTimeField(null=True, blank=True)
    appointment_day = models.DateTimeField(null=True, blank=True)

    sms_received = models.BooleanField(default=False)

    # Dataset uses "No-show": Yes means the patient did not attend.
    # This field stores the opposite: True means the patient attended.
    showed_up = models.BooleanField(default=True)

    # Difference in days between scheduled date and appointment date.
    date_difference = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["showed_up"]),
            models.Index(fields=["sms_received"]),
            models.Index(fields=["appointment_day"]),
            models.Index(fields=["date_difference"]),
            models.Index(fields=["showed_up", "sms_received"]),
        ]

    def __str__(self):
        return f"Appointment {self.appointment_id}"