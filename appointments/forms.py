from django import forms
from .models import Patient


# Django form used to add a new patient through the website.
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient

        # Fields shown on the patient registration form.
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
            # Limit the handicap input shown in the browser.
            # Validation is still performed below because users
            # can bypass HTML input restrictions.
            'handicap': forms.NumberInput(attrs={'min': 0, 'max': 1}),
        }

    # This makes sure the age entered is not negative.
    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age is not None and age < 0:
            raise forms.ValidationError("Age cannot be negative.")

        return age

    # Only allow the values by the dataset.
    def clean_gender(self):
        gender = self.cleaned_data.get('gender')

        if gender not in ['M', 'F']:
            raise forms.ValidationError("Gender must be M or F.")

        return gender

    # Check that the handicap value is within the allowed range.
    def clean_handicap(self):
        handicap = self.cleaned_data.get('handicap')

        if handicap is not None and not (0 <= handicap <= 1):
            raise forms.ValidationError("Handicap must be 0 or 1.")

        return handicap