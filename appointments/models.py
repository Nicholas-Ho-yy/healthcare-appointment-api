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

    # The dataset may contain unusual ages, so the model
    # limits the value to a realistic maximum of 120.
    age = models.PositiveSmallIntegerField(validators=[MaxValueValidator(120)])

    scholarship = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    alcoholism = models.BooleanField(default=False)

    # The dataset stores handicap as a number from 0 to 4,
    # rather than as a simple True or False value.
    handicap = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(4)]
    )

    class Meta:
        ordering = ["id"]

        # These fields are used often when filtering patients,
        # so indexes help the database find matching records faster.
        indexes = [
            models.Index(fields=["age"]),
            models.Index(fields=["gender"]),
        ]

    def __str__(self):
        return f"Patient {self.patient_id}"


class Neighbourhood(models.Model):
    """
    Stores each neighbourhood once so it can be reused
    by multiple appointment records.
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

    # Delete a patient's appointments if the patient is removed.
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    # Delete related appointments if a neighbourhood is removed.
    neighbourhood = models.ForeignKey(
        Neighbourhood,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    scheduled_day = models.DateTimeField(null=True, blank=True)
    appointment_day = models.DateTimeField(null=True, blank=True)

    sms_received = models.BooleanField(default=False)

    # The source dataset uses a "No-show" field.
    # This model stores the opposite, so True means the patient attended.
    showed_up = models.BooleanField(default=True)

    # Stores the number of days between scheduling
    # the appointment and the actual appointment date.
    date_difference = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

        # These indexes support the fields most often used
        # by the appointment filtering endpoint.
        indexes = [
            models.Index(fields=["showed_up"]),
            models.Index(fields=["sms_received"]),
            models.Index(fields=["appointment_day"]),
            models.Index(fields=["date_difference"]),
            models.Index(fields=["showed_up", "sms_received"]),
        ]

    def __str__(self):
        return f"Appointment {self.appointment_id}"