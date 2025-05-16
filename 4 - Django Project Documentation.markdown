# SmartJobPortal Django Project Documentation

## Overview

This documentation tracks the development of **SmartJobPortal**, a Django web application designed to facilitate job listings, user authentication, employer/seeker dashboards, and utility functions. The project leverages Django's modularity to create a scalable and maintainable job portal website. This document will be updated as new features, models, views, or configurations are implemented.

## Project Setup

### Prerequisites

- Python 3.8 or higher
- Django 5.1 or higher
- pip (Python package manager)
- Virtualenv (recommended for isolating dependencies)

### Installation

1. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Django**:

   ```bash
   pip install django
   ```

3. **Create the Django project**:

   ```bash
   django-admin startproject smartjobportal
   cd smartjobportal
   ```

4. **Create custom apps**:
   The project is modularized into four apps to separate concerns:

   ```bash
   python manage.py startapp accounts    # Handles authentication and user model
   python manage.py startapp jobs        # Handles job listings and applications
   python manage.py startapp dashboard   # Separate views for employer/seeker
   python manage.py startapp core        # Utilities like decorators, pagination, email
   ```

5. **Register apps**:
   Update `smartjobportal/settings.py` to include the custom apps:

   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       # Our custom apps
       'accounts',
       'jobs',
       'dashboard',
       'core',
   ]
   ```

6. **Apply migrations and run the server**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   Access the site at `http://127.0.0.1:8000/` to verify the Django welcome page loads.

### Project Structure

```
smartjobportal/
├── manage.py
├── smartjobportal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── tokens.py
│   ├── urls.py
│   └── views.py
├── jobs/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── dashboard/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── templates/
│   └── accounts/
│       ├── activation_email.html
│       ├── login.html
│       ├── password_reset.html
│       ├── password_reset_complete.html
│       ├── password_reset_confirm.html
│       ├── password_reset_done.html
│       ├── please_check_email.html
│       └── register.html
    └── dashboard/
│       ├── employer_dashboard.html
│       ├── seeker_dashboard.html
│       ├── unknown_role.html
    └── jobs/
│       ├── apply_job.html
│       ├── job_detail.html
│       ├── job_list.html
    └── base.html
│       
└── docs/
    └── index.md  # This documentation
```

## Features

### Step 1: Project Initialization

- **Goal**: Set up the Django project structure and create initial apps.
- **Actions**:
  - Created the `smartjobportal` Django project.
  - Initialized four apps:
    - `accounts`: Manages user authentication and user models.
    - `jobs`: Handles job listings and applications.
    - `dashboard`: Provides separate views for employers and job seekers.
    - `core`: Contains utilities like decorators, pagination, and email functionality.
  - Registered apps in `INSTALLED_APPS` in `settings.py`.
  - Applied initial migrations and tested the development server.
- **Outcome**:
  - Project directory and apps successfully created.
  - Apps added to `INSTALLED_APPS`.
  - Development server runs without errors, displaying the Django welcome page at `http://127.0.0.1:8000/`.

### Step 2: Custom User Model (accounts app)

- **Goal**: Create a custom user model to support different roles: Job Seeker and Employer.
- **Actions**:

  1. **Defined the CustomUser model**:
     Updated `accounts/models.py` to extend `AbstractUser` and include role-based flags:

     ```python
     from django.contrib.auth.models import AbstractUser
     from django.db import models

     class CustomUser(AbstractUser):
         is_employer = models.BooleanField(default=False)
         is_seeker = models.BooleanField(default=False)

         def __str__(self):
             return self.username
     ```

     This model differentiates users by `is_employer` and `is_seeker` flags.

  2. **Configured Django to use the custom user model**:
     Added the following to `smartjobportal/settings.py`:

     ```python
     AUTH_USER_MODEL = 'accounts.CustomUser'
     ```

     This replaces Django’s default user model with `CustomUser`.

  3. **Created and applied migrations**:
     Ran the following commands to generate and apply migrations for the `accounts` app:

     ```bash
     python manage.py makemigrations accounts
     python manage.py migrate
     ```

     _Note_: These migrations were applied early to avoid conflicts with the custom user model.

  4. **Registered the model in the admin panel**:
     Updated `accounts/admin.py` to include `CustomUser` in the Django admin interface:

     ```python
     from django.contrib import admin
     from django.contrib.auth.admin import UserAdmin
     from .models import CustomUser

     admin.site.register(CustomUser, UserAdmin)
     ```

     This allows management of `CustomUser` instances via the admin panel.

- **Outcome**:
  - `CustomUser` model created with `is_employer` and `is_seeker` flags.
  - `AUTH_USER_MODEL` set to `accounts.CustomUser` in `settings.py`.
  - Migrations successfully created and applied.
  - `CustomUser` registered in the admin panel for easy management.

### Step 3: Authentication System

- **Goal**: Enable users to register, log in, and log out, with the ability to choose their role (Job Seeker or Employer) during registration.
- **Actions**:

  1. **Created a custom registration form**:
     Added `accounts/forms.py` to define a form for user registration, extending Django’s `UserCreationForm`:

     ```python
     from django import forms
     from django.contrib.auth.forms import UserCreationForm
     from .models import CustomUser

     class CustomUserCreationForm(UserCreationForm):
         is_employer = forms.BooleanField(required=False, label='Register as Employer')
         is_seeker = forms.BooleanField(required=False, label='Register as Job Seeker')

         class Meta:
             model = CustomUser
             fields = ['username', 'email', 'password1', 'password2', 'is_employer', 'is_seeker']
     ```

  2. **Implemented registration view**:
     Updated `accounts/views.py` to handle user registration and automatic login:

     ```python
     from django.shortcuts import render, redirect
     from django.contrib.auth import authenticate, login
     from django.contrib.auth.views import LoginView, LogoutView
     from .forms import CustomUserCreationForm

     def register_view(request):
         if request.method == 'POST':
             form = CustomUserCreationForm(request.POST)
             if form.is_valid():
                 user = form.save()
                 login(request, user)
                 return redirect('dashboard')
         else:
             form = CustomUserCreationForm()
         return render(request, 'accounts/register.html', {'form': form})
     ```

  3. **Configured URLs**:

     - Created `accounts/urls.py`:

       ```python
       from django.urls import path
       from django.contrib.auth import views as auth_views
       from .views import register_view

       urlpatterns = [
           path('register/', register_view, name='register'),
           path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
           path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
       ]
       ```

     - Updated `smartjobportal/urls.py`:

       ```python
       from django.contrib import admin
       from django.urls import path, include

       urlpatterns = [
           path('admin/', admin.site.urls),
           path('accounts/', include('accounts.urls')),
       ]
       ```

  4. **Created templates**:

     - `templates/accounts/register.html`:
       ```html
       <h2>Register</h2>
       <form method="post">
         {% csrf_token %} {{ form.as_p }}
         <button type="submit">Register</button>
       </form>
       <a href="{% url 'login' %}">Already have an account?</a>
       ```
     - `templates/accounts/login.html`:
       ```html
       <h2>Login</h2>
       <form method="post">
         {% csrf_token %} {{ form.as_p }}
         <button type="submit">Login</button>
       </form>
       <a href="{% url 'register' %}">Don’t have an account?</a>
       ```

  5. **Updated settings**:
     - Added to `smartjobportal/settings.py`:
       ```python
       LOGIN_REDIRECT_URL = 'dashboard'
       LOGOUT_REDIRECT_URL = 'login'
       import os
       TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'templates')]
       ```

- **Outcome**:
  - Users can register at `/accounts/register/`, log in at `/accounts/login/`, and log out at `/accounts/logout/`.
  - Registration redirects to `dashboard` (to be defined).
  - Login redirects to `dashboard`, logout to `login`.

### Step 4: Email Verification and Password Reset

- **Goal**: Implement email verification for new registrations and a password reset system.
- **Actions**:

  #### Part 1: Email Verification on Registration

  1. **Configured email settings**:
     Updated `smartjobportal/settings.py` to enable email sending via Gmail SMTP:

     ```python
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     EMAIL_HOST = 'smtp.gmail.com'
     EMAIL_PORT = 587
     EMAIL_USE_TLS = True
     EMAIL_HOST_USER = 'your-email@gmail.com'
     EMAIL_HOST_PASSWORD = 'your-app-password'  # Use Gmail App Password
     ```

     _Note_: Requires enabling "App Passwords" in Gmail at https://myaccount.google.com/apppasswords.

  2. **Created email verification token generator**:
     Added `accounts/tokens.py` to define a token generator for email verification:

     ```python
     from django.contrib.auth.tokens import PasswordResetTokenGenerator

     class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
         pass

     account_activation_token = EmailVerificationTokenGenerator()
     ```

  3. **Updated registration view for email verification**:
     Modified `accounts/views.py` to send a verification email after registration:

     ```python
     from django.contrib.sites.shortcuts import get_current_site
     from django.template.loader import render_to_string
     from django.utils.http import urlsafe_base64_encode
     from django.utils.encoding import force_bytes
     from django.core.mail import EmailMessage
     from .tokens import account_activation_token
     from django.shortcuts import render, redirect
     from django.contrib.auth import authenticate, login
     from django.contrib.auth.views import LoginView, LogoutView
     from .forms import CustomUserCreationForm

     def register_view(request):
         if request.method == 'POST':
             form = CustomUserCreationForm(request.POST)
             if form.is_valid():
                 user = form.save(commit=False)
                 user.is_active = False  # Disable account until confirmed
                 user.save()
                 current_site = get_current_site(request)
                 mail_subject = 'Activate your Smart Job Portal account'
                 message = render_to_string('accounts/activation_email.html', {
                     'user': user,
                     'domain': current_site.domain,
                     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                     'token': account_activation_token.make_token(user),
                 })
                 to_email = form.cleaned_data.get('email')
                 email = EmailMessage(mail_subject, message, to=[to_email])
                 email.send()
                 return render(request, 'accounts/please_check_email.html')
         else:
             form = CustomUserCreationForm()
         return render(request, 'accounts/register.html', {'form': form})
     ```

  4. **Added activation view**:
     Added to `accounts/views.py` to handle account activation via email link:

     ```python
     from django.utils.http import urlsafe_base64_decode
     from django.contrib.auth import get_user_model
     from django.http import HttpResponse

     def activate_account(request, uidb64, token):
         try:
             uid = urlsafe_base64_decode(uidb64).decode()
             user = get_user_model().objects.get(pk=uid)
         except:
             user = None

         if user is not None and account_activation_token.check_token(user, token):
             user.is_active = True
             user.save()
             login(request, user)
             return redirect('dashboard')
         else:
             return HttpResponse('Activation link is invalid!')
     ```

  5. **Updated URLs for activation**:
     Modified `accounts/urls.py` to include the activation route:

     ```python
     from django.urls import path
     from django.contrib.auth import views as auth_views
     from .views import register_view, activate_account

     urlpatterns = [
         path('register/', register_view, name='register'),
         path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
         path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
         path('activate/<uidb64>/<token>/', activate_account, name='activate'),
     ]
     ```

  6. **Created activation email template**:
     Added `templates/accounts/activation_email.html`:

     ```html
     Hi {{ user.username }}, Click the link below to activate your account:
     http://{{ domain }}{% url 'activate' uidb64=uid token=token %} If you
     didn’t request this, please ignore this email.
     ```

  7. **Created confirmation page**:
     Added `templates/accounts/please_check_email.html`:
     ```html
     <h2>Thank you for registering!</h2>
     <p>Please check your email to activate your account.</p>
     ```

  #### Part 2: Password Reset

  8. **Added password reset URLs**:
     Updated `accounts/urls.py` to include Django’s built-in password reset views:

     ```python
     from django.urls import path
     from django.contrib.auth import views as auth_views
     from .views import register_view, activate_account

     urlpatterns = [
         path('register/', register_view, name='register'),
         path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
         path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
         path('activate/<uidb64>/<token>/', activate_account, name='activate'),
         path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
         path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
         path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
         path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
     ]
     ```

  9. **Created password reset templates**:
     - `templates/accounts/password_reset.html`:
       ```html
       <h2>Reset your password</h2>
       <form method="post">
         {% csrf_token %} {{ form.as_p }}
         <button type="submit">Send reset email</button>
       </form>
       ```
     - `templates/accounts/password_reset_done.html`:
       ```html
       <p>We've emailed you instructions for setting your password.</p>
       ```
     - `templates/accounts/password_reset_confirm.html`:
       ```html
       <h2>Enter new password</h2>
       <form method="post">
         {% csrf_token %} {{ form.as_p }}
         <button type="submit">Reset password</button>
       </form>
       ```
     - `templates/accounts/password_reset_complete.html`:
       ```html
       <p>
         Your password has been reset. <a href="{% url 'login' %}">Log in</a>
       </p>
       ```

- **Outcome**:
  - **Email Verification**:
    - Users register at `/accounts/register/` and receive an email with an activation link.
    - Accounts are inactive (`is_active=False`) until verified.
    - Clicking the activation link at `/accounts/activate/<uidb64>/<token>/` activates the account, logs the user in, and redirects to `dashboard`.
    - A confirmation page at `/accounts/please_check_email/` informs users to check their email.
  - **Password Reset**:
    - Users can request a password reset at `/accounts/password_reset/`.
    - An email with reset instructions is sent, followed by a confirmation page.
    - Users set a new password at `/accounts/reset/<uidb64>/<token>/` and are redirected to a completion page.
    - The flow uses Django’s built-in password reset system with custom templates.
  - All templates and URLs are properly configured for a secure and user-friendly experience.

## Configuration

- **Database**: Default SQLite (configurable in `settings.py`).
- **Static Files**: Configured for development (update for production as needed).
- **Templates**: Custom templates directory configured at `templates/`.
- **Authentication**:
  - Custom user model (`accounts.CustomUser`) supports role-based users.
    jargons
  - Authentication system supports registration, login, logout, email verification, and password reset.
  - Redirects configured for login (`dashboard`), logout (`login`), and activation (`dashboard`).
- **Email**:
  - Configured to use Gmail SMTP for sending verification and password reset emails.
  - Requires a Gmail App Password for secure access.

## Usage

- **Register**: Navigate to `/accounts/register/` to create an account, selecting Job Seeker or Employer. Check email for an activation link.
- **Activate Account**: Click the link in the verification email to activate the account and log in.
- **Login**: Access `/accounts/login/` to sign in.
- **Logout**: Visit `/accounts/logout/` to sign out.
- **Password Reset**: Go to `/accounts/password_reset/` to request a password reset email.
- _Note_: The `dashboard` redirect URL will be functional once implemented.

## Development Notes

- **Version Control**: Use Git for tracking changes.
- **Testing**: Write unit tests in `tests.py` for authentication, email verification, and password reset (to be added).
- **Deployment**:
  - Update `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` for production.
  - Consider using a transactional email service (e.g., SendGrid) for production.
- **Security**:
  - Ensure CSRF tokens are included in all forms.
  - Use a secure App Password for Gmail in development.
  - Verify `django.contrib.sites` is configured with the correct domain for production.
- **Important**:
  - The `dashboard` URL is referenced but not yet defined.
  - Ensure the `django.contrib.sites` app is added to `INSTALLED_APPS` and `SITE_ID` is set in `settings.py` for `get_current_site` to work.

## Next Steps

_Please provide details about the next features or components you’ve built (e.g., dashboard implementation, job models, or additional functionality), and this documentation will be updated accordingly._
