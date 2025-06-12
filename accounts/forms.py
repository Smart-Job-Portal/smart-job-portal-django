from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Register as'
    )
    profile_image = forms.ImageField(
        label="Profile Picture (optional)",
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'profile_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'role':
                continue  # Already styled in widget init
            elif field_name == 'profile_image':
                field.widget.attrs.update({'class': 'form-control-file'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Enter a valid email address.")
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.is_employer = (role == 'employer')
        user.is_seeker = (role == 'seeker')
        if commit:
            user.save()
            # Update UserProfile with profile_image if provided
            profile_image = self.cleaned_data.get('profile_image')
            if profile_image:
                # If signals already create UserProfile, just update
                profile = getattr(user, 'userprofile', None)
                if profile:
                    profile.image = profile_image
                    profile.save()
        return user
