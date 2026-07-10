import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime

from appointments.models import Patient, Neighbourhood, Appointment


# Maximum number of rows to import (assignment requirement)
MAX_ROWS = 10000


def to_bool(value):
    """
    Convert CSV boolean-like values into Python booleans.
    """
    return str(value).strip().lower() in ["1", "true", "yes"]


def to_int(value):
    """
    Convert CSV numeric/boolean-like values into integers.
    """

    value = str(value).strip()

    if value.lower() in ["true", "yes"]:
        return 1

    if value.lower() in ["false", "no", ""]:
        return 0

    return int(value)


class Command(BaseCommand):
    help = "Load Healthcare Appointment No-Show dataset into the database"

    def handle(self, *args, **kwargs):

        # Locate the CSV file inside the project's data folder.
        csv_path = (
            Path(settings.BASE_DIR)
            / "data"
            / "healthcare_noshows.csv"
        )

        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f"CSV file not found: {csv_path}")
            )
            return

        imported = 0
        skipped = 0

        # Wrap the entire import inside one transaction.
        # If any unexpected error occurs, everything rolls back.
        with transaction.atomic():

            # -------------------------------------------------------
            # Reset database before loading.
            # This was specifically requested in the lecturer feedback.
            # Delete Appointment records first because they depend on
            # Patient and Neighbourhood through foreign keys.
            # -------------------------------------------------------
            self.stdout.write("Removing existing data...")

            Appointment.objects.all().delete()
            Patient.objects.all().delete()
            Neighbourhood.objects.all().delete()

            self.stdout.write(
                self.style.SUCCESS("Database successfully reset.")
            )

            # -------------------------------------------------------
            # Read the CSV file.
            # -------------------------------------------------------
            with open(csv_path, newline="", encoding="utf-8") as csv_file:

                reader = csv.DictReader(csv_file)

                for row in reader:

                    # Stop after importing the first 10,000 rows.
                    if imported >= MAX_ROWS:
                        break

                    try:

                        # Create patient if it does not already exist.
                        patient, _ = Patient.objects.get_or_create(
                            patient_id=row["PatientId"],
                            defaults={
                                "gender": row["Gender"],
                                "age": to_int(row["Age"]),
                                "scholarship": to_bool(row["Scholarship"]),
                                "hypertension": to_bool(row["Hipertension"]),
                                "diabetes": to_bool(row["Diabetes"]),
                                "alcoholism": to_bool(row["Alcoholism"]),
                                "handicap": to_int(row["Handcap"]),
                            },
                        )

                        # Create neighbourhood if it does not already exist.
                        neighbourhood, _ = Neighbourhood.objects.get_or_create(
                            name=row["Neighbourhood"]
                        )

                        # Create appointment record.
                        Appointment.objects.create(
                            appointment_id=row["AppointmentID"],
                            patient=patient,
                            neighbourhood=neighbourhood,
                            scheduled_day=parse_datetime(
                                row["ScheduledDay"]
                            ),
                            appointment_day=parse_datetime(
                                row["AppointmentDay"]
                            ),
                            sms_received=to_bool(
                                row["SMS_received"]
                            ),
                            showed_up=to_bool(
                                row["Showed_up"]
                            ),
                            date_difference=to_int(
                                row["Date.diff"]
                            ),
                        )

                        imported += 1

                    except (ValueError, KeyError) as error:

                        skipped += 1

                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipped row {reader.line_num}: {error}"
                            )
                        )

                        continue

        self.stdout.write(
            self.style.SUCCESS(
                f"\nImport completed successfully!\n"
                f"Imported records: {imported}\n"
                f"Skipped records : {skipped}"
            )
        )