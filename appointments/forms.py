from django import forms
from .models import Patient


# Form used to create new patient records through the web interface.
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'patient_id',
            'gender',
            'age',
            'scholarship',
            'hypertension',
            'diabetes',
            'alcoholism',
            'handicap',
        ]
        widgets = {
            # Browser-level hint only -- the real enforcement still happens
            # in clean_handicap() below, since HTML min/max attributes can
            # be bypassed (e.g. by editing the DOM or submitting via curl).
            'handicap': forms.NumberInput(attrs={'min': 0, 'max': 1}),
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age is not None and age < 0:
            raise forms.ValidationError("Age cannot be negative.")

        return age

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')

        if gender not in ['M', 'F']:
            raise forms.ValidationError("Gender must be M or F.")

        return gender

    def clean_handicap(self):
        handicap = self.cleaned_data.get('handicap')

        if handicap is not None and not (0 <= handicap <= 1):
            raise forms.ValidationError("Handicap must be 0 or 1.")

        return handicap