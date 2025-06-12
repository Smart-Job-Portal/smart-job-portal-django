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
        # Consistent Bootstrap styling
        for name, field in self.fields.items():
            if name == 'role':
                continue  # RadioSelect styled in field definition
            elif name == 'profile_image':
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
            # Uniqueness check
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        """
        Saves the user and links profile_image to the user's profile if provided.
        Defensive for edge-cases: supports both with/without profile signal.
        """
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.is_employer = (role == 'employer')
        user.is_seeker = (role == 'seeker')
        if commit:
            user.save()
            profile_image = self.cleaned_data.get('profile_image')
            # Try to get, else create the profile (defensive for signal race condition)
            profile, created = UserProfile.objects.get_or_create(user=user)
            if profile_image:
                profile.image = profile_image
                profile.save()
        return user
from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'bio', 'resume']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['resume'].widget.attrs.update({'class': 'form-control-file'})