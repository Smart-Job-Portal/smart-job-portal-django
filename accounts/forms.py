from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    is_employer = forms.BooleanField(required=False, label='Register as Employer')
    is_seeker = forms.BooleanField(required=False, label='Register as Job Seeker')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_employer', 'is_seeker']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name in ['is_employer', 'is_seeker']:
                self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})  # Checkboxes
            else:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})  # Regular inputs

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        is_employer = cleaned_data.get("is_employer")
        is_seeker = cleaned_data.get("is_seeker")

        if is_employer and is_seeker:
            raise forms.ValidationError("You cannot register as both Employer and Job Seeker.")
        if not is_employer and not is_seeker:
            raise forms.ValidationError("Please select either Employer or Job Seeker.")

        return cleaned_data
