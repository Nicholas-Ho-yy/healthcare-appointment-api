from rest_framework import serializers
from .models import Patient, Neighbourhood, Appointment


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    """
    Hyperlinked serializer for Patient records.
    The url field allows API users to navigate directly to each patient detail endpoint.
    """

    appointments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="appointment-detail"
    )

    class Meta:
        model = Patient
        fields = [
            "url",
            "id",
            "patient_id",
            "gender",
            "age",
            "scholarship",
            "hypertension",
            "diabetes",
            "alcoholism",
            "handicap",
            "appointments",
        ]

    def validate_age(self, value):
        if value < 0:
            raise serializers.ValidationError("Age cannot be negative.")
        return value


class NeighbourhoodSerializer(serializers.HyperlinkedModelSerializer):
    """
    Hyperlinked serializer for neighbourhood records.
    """

    appointments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="appointment-detail"
    )

    class Meta:
        model = Neighbourhood
        fields = [
            "url",
            "id",
            "name",
            "appointments",
        ]


class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Hyperlinked serializer for Appointment records.

    patient and neighbourhood are represented as hyperlinks instead of plain IDs,
    which meets the Django REST Framework hyperlinked serializer requirement.
    """

    patient = serializers.HyperlinkedRelatedField(
        queryset=Patient.objects.all(),
        view_name="patient-detail"
    )

    neighbourhood = serializers.HyperlinkedRelatedField(
        queryset=Neighbourhood.objects.all(),
        view_name="neighbourhood-detail"
    )

    class Meta:
        model = Appointment
        fields = [
            "url",
            "id",
            "appointment_id",
            "patient",
            "neighbourhood",
            "scheduled_day",
            "appointment_day",
            "sms_received",
            "showed_up",
            "date_difference",
        ]

    def validate(self, data):
        scheduled = data.get(
            "scheduled_day",
            getattr(self.instance, "scheduled_day", None)
        )
        appointment = data.get(
            "appointment_day",
            getattr(self.instance, "appointment_day", None)
        )

        if scheduled and appointment and appointment < scheduled:
            raise serializers.ValidationError(
                "Appointment day cannot be before the scheduled day."
            )

        return data