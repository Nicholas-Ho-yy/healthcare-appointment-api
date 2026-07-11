import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime

from appointments.models import Patient, Neighbourhood, Appointment


# Only import the first 10,000 rows, as required by the assignment.
MAX_ROWS = 10000


def to_bool(value):
    """
    Convert values such as 1, true, and yes into a Boolean.
    """
    return str(value).strip().lower() in ["1", "true", "yes"]


def to_int(value):
    """
    Convert CSV values into integers.

    Some columns use true and false instead of 1 and 0,
    so these values are handled before converting to an integer.
    """
    value = str(value).strip()

    if value.lower() in ["true", "yes"]:
        return 1

    if value.lower() in ["false", "no", ""]:
        return 0

    return int(value)


class Command(BaseCommand):
    """
    Load healthcare appointment data from the CSV file.

    The command clears the existing records first so that running
    the import again does not create any duplicate data.
    """

    help = "Load Healthcare Appointment No-Show dataset into the database"

    def handle(self, *args, **kwargs):

        # Locate the CSV file inside the project's data folder.
        csv_path = (
            Path(settings.BASE_DIR)
            / "data"
            / "healthcare_noshows.csv"
        )

        # Stop the command and show an error if the CSV cannot be found.
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f"CSV file not found: {csv_path}")
            )
            return

        imported = 0
        skipped = 0

        # Keep the reset and import inside one transaction.
        # If an unexpected error occurs, Django can roll back the changes.
        with transaction.atomic():


            # Reset database before loading.
            # Delete Appointment records first because they depend on
            # Patient and Neighbourhood through foreign keys.
            self.stdout.write("Removing existing data...")

            Appointment.objects.all().delete()
            Patient.objects.all().delete()
            Neighbourhood.objects.all().delete()

            self.stdout.write(
                self.style.SUCCESS("Database successfully reset.")
            )

            # Open the CSV and process one row at a time.
            with open(csv_path, newline="", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)

                for row in reader:
                    # Stop once 10,000 rows have been imported.
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

                        # Create the appointment and connect it to
                        # the related patient and neighbourhood.
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
                        # Skip bad rows instead of stopping the full import.
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