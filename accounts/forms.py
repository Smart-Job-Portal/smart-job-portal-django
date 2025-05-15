from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    is_employer = forms.BooleanField(required=False, label='Register as Employer')
    is_seeker = forms.BooleanField(required=False, label='Register as Job Seeker')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_employer', 'is_seeker']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    is_employer = forms.BooleanField(required=False, label='Register as Employer')
    is_seeker = forms.BooleanField(required=False, label='Register as Job Seeker')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_employer', 'is_seeker']
