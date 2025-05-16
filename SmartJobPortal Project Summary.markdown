# SmartJobPortal Project Summary

## Overview
**SmartJobPortal** is a Django-based web application designed to connect job seekers and employers. It allows users to register as either job seekers or employers, browse and apply for jobs, manage job postings, and view role-specific dashboards. The project is modular, with separate apps for authentication (`accounts`), job management (`jobs`), dashboards (`dashboard`), and utilities (`core`). This document summarizes the development progress for future reference and presentation purposes, covering setup, features, models, views, templates, and configurations as of May 15, 2025.

## Project Setup
- **Framework**: Django 5.1+, Python 3.8+
- **Apps Created**:
  - `accounts`: Manages user authentication and custom user model.
  - `jobs`: Handles job postings and applications.
  - `dashboard`: Provides role-specific dashboards for employers and seekers.
  - `core`: Reserved for utilities (e.g., decorators, pagination, email).
- **Installation Steps**:
  1. Created virtual environment: `python -m venv venv`
  2. Installed Django: `pip install django`
  3. Started project: `django-admin startproject smartjobportal`
  4. Created apps: `python manage.py startapp <app_name>`
  5. Registered apps in `settings.py`:
     ```python
     INSTALLED_APPS = [
         'django.contrib.admin',
         'django.contrib.auth',
         'django.contrib.contenttypes',
         'django.contrib.sessions',
         'django.contrib.messages',
         'django.contrib.staticfiles',
         'django.contrib.sites',
         'accounts',
         'jobs',
         'dashboard',
         'core',
     ]
     SITE_ID = 1
     ```
  6. Applied migrations: `python manage.py migrate`
  7. Ran server: `python manage.py runserver`

- **Directory Structure**:
  ```
  smartjobportal/
  ├── manage.py
  ├── smartjobportal/
  │   ├── settings.py
  │   ├── urls.py
  │   ├── asgi.py
  │   └── wsgi.py
  ├── accounts/
  │   ├── forms.py
  │   ├── models.py
  │   ├── tokens.py
  │   ├── urls.py
  │   ├── views.py
  ├── jobs/
  │   ├── models.py
  │   ├── urls.py
  │   ├── views.py
  ├── dashboard/
  │   ├── urls.py
  │   ├── views.py
  ├── core/
  ├── templates/
  │   ├── accounts/
  │   │   ├── activation_email.html
  │   │   ├── login.html
  │   │   ├── password_reset*.html
  │   │   ├── please_check_email.html
  │   │   ├── register.html
  │   ├── jobs/
  │   │   ├── job_list.html
  │   │   ├── job_detail.html
  │   │   ├── job_form.html
  │   │   ├── job_confirm_delete.html
  │   │   ├── apply_job.html
  │   ├── dashboard/
  │   │   ├── employer_dashboard.html
  │   │   ├── seeker_dashboard.html
  │   ├── base.html
  ```

## Features Implemented

### 1. Custom User Model (`accounts` app)
- **Purpose**: Support two user roles: Job Seeker and Employer.
- **Model**: `CustomUser` in `accounts/models.py`:
  ```python
  from django.contrib.auth.models import AbstractUser
  from django.db import models

  class CustomUser(AbstractUser):
      is_employer = models.BooleanField(default=False)
      is_seeker = models.BooleanField(default=False)

      def __str__(self):
          return self.username
  ```
- **Configuration**:
  - Set `AUTH_USER_MODEL = 'accounts.CustomUser'` in `settings.py`.
  - Registered in `accounts/admin.py` for admin panel access.
  - Applied migrations: `python manage.py makemigrations accounts; python manage.py migrate`

### 2. Authentication System
- **Purpose**: Enable registration, login, logout, email verification, and password reset.
- **Registration Form**: `CustomUserCreationForm` in `accounts/forms.py`:
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
          widgets = {
              'username': forms.TextInput(attrs={'class': 'form-control'}),
              'email': forms.EmailInput(attrs={'class': 'form-control'}),
              'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
              'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
              'is_employer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
              'is_seeker': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
          }
  ```
- **Views** (`accounts/views.py`):
  - `register_view`: Handles registration with email verification.
  - `activate_account`: Activates accounts via emailed links.
- **URLs** (`accounts/urls.py`):
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
- **Email Verification**:
  - Configured Gmail SMTP in `settings.py`:
    ```python
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your-app-password'
    ```
  - Created `accounts/tokens.py` for verification tokens.
  - Templates: `activation_email.html`, `please_check_email.html`.
- **Templates**:
  - `register.html`: Styled with Bootstrap, uses `needs-validation` for client-side validation, and custom checkbox styling for roles.
  - `login.html`: Bootstrap-styled login form with links to register and reset password.
  - Password reset templates: `password_reset.html`, `password_reset_done.html`, `password_reset_confirm.html`, `password_reset_complete.html`.
- **Outcome**:
  - Users register at `/accounts/register/`, verify email, log in at `/accounts/login/`, and log out at `/accounts/logout/`.
  - Password reset available at `/accounts/password_reset/`.

### 3. Job Management (`jobs` app)
- **Purpose**: Allow employers to create, update, delete, and publish job postings; seekers to browse and apply.
- **Models** (`jobs/models.py`):
  ```python
  from django.db import models
  from django.conf import settings

  class ActiveJobManager(models.Manager):
      def get_queryset(self):
          return super().get_queryset().filter(published=True)

  class Job(models.Model):
      employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
      title = models.CharField(max_length=255)
      description = models.TextField()
      location = models.CharField(max_length=255)
      salary = models.DecimalField(max_digits=10, decimal_places=2)
      posted_on = models.DateTimeField(auto_now_add=True)
      published = models.BooleanField(default=False)
      objects = models.Manager()
      active_jobs = ActiveJobManager()

      def __str__(self):
          return self.title

  class Application(models.Model):
      job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
      seeker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
      resume = models.FileField(upload_to='resumes/')
      applied_on = models.DateTimeField(auto_now_add=True)

      def __str__(self):
          return f"{self.seeker.username} applied for {self.job.title}"
  ```
- **URLs** (`jobs/urls.py`):
  ```python
  from django.urls import path
  from .views import JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView, apply_job

  urlpatterns = [
      path('', JobListView.as_view(), name='job_list'),
      path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
      path('create/', JobCreateView.as_view(), name='job_create'),
      path('<int:pk>/update/', JobUpdateView.as_view(), name='job_update'),
      path('<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
      path('<int:job_id>/apply/', apply_job, name='apply_job'),
  ]
  ```
- **Views** (`jobs/views.py`):
  ```python
  from django.shortcuts import render, get_object_or_404, redirect
  from django.contrib.auth.decorators import login_required
  from .models import Job, Application
  from django.http import HttpResponseForbidden
  from django.views.generic import ListView, DetailView
  from django.views.generic.edit import CreateView, UpdateView, DeleteView
  from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
  from django.urls import reverse_lazy

  class JobListView(ListView):
      model = Job
      template_name = 'jobs/job_list.html'
      context_object_name = 'jobs'
      ordering = ['-posted_on']
      paginate_by = 2

      def get_queryset(self):
          return Job.active_jobs.all()

  class JobDetailView(DetailView):
      model = Job
      template_name = 'jobs/job_detail.html'
      context_object_name = 'job'

  class JobCreateView(LoginRequiredMixin, CreateView):
      model = Job
      template_name = 'jobs/job_form.html'
      fields = ['title', 'description', 'location', 'salary']
      success_url = reverse_lazy('job_list')

      def form_valid(self, form):
          form.instance.employer = self.request.user
          return super().form_valid(form)

  class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
      model = Job
      template_name = 'jobs/job_form.html'
      fields = ['title', 'description', 'location', 'salary']
      success_url = reverse_lazy('job_list')

      def test_func(self):
          job = self.get_object()
          return self.request.user == job.employer

  class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
      model = Job
      template_name = 'jobs/job_confirm_delete.html'
      success_url = reverse_lazy('job_list')

      def test_func(self):
          job = self.get_object()
          return self.request.user == job.employer

  @login_required
  def apply_job(request, job_id):
      if not request.user.is_seeker:
          return HttpResponseForbidden("You are not allowed to apply for jobs.")
      job = get_object_or_404(Job, id=job_id)
      if request.method == 'POST':
          resume = request.FILES.get('resume')
          Application.objects.create(job=job, seeker=request.user, resume=resume)
          return redirect('job_detail', job_id=job.id)
      return render(request, 'jobs/apply_job.html', {'job': job})
  ```
- **Templates**:
  - `job_list.html`: Lists published jobs with pagination (2 per page), includes "Back to Employer Dashboard" for employers.
  - `job_detail.html`: Shows job details and application form for seekers.
  - `job_form.html`: Form for creating/editing jobs, dynamically titled.
  - `job_confirm_delete.html`: Confirms job deletion.
  - `apply_job.html`: Form for seekers to upload resumes.
- **Outcome**:
  - Employers create jobs at `/jobs/create/`, edit at `/jobs/<pk>/update/`, delete at `/jobs/<pk>/delete/`.
  - Only published jobs (`published=True`) appear in `/jobs/` via `ActiveJobManager`.
  - Seekers apply at `/jobs/<job_id>/apply/` with resume uploads.
  - Pagination enhances user experience.

### 4. Dashboards (`dashboard` app)
- **Purpose**: Provide role-specific views for employers (jobs posted, applications received) and seekers (applications submitted).
- **View** (`dashboard/views.py`):
  ```python
  from django.shortcuts import render
  from django.contrib.auth.decorators import login_required
  from jobs.models import Job, Application

  @login_required
  def dashboard_view(request):
      user = request.user
      if hasattr(user, 'is_employer') and user.is_employer:
          jobs = Job.objects.filter(employer=user)
          applications = Application.objects.filter(job__employer=user).select_related('job', 'seeker')
          context = {'jobs': jobs, 'applications': applications}
          return render(request, 'dashboard/employer_dashboard.html', context)
      elif hasattr(user, 'is_seeker') and user.is_seeker:
          applications = Application.objects.filter(seeker=user).select_related('job')
          context = {'applications': applications}
          return render(request, 'dashboard/seeker_dashboard.html', context)
      else:
          return render(request, 'dashboard/unknown_role.html')
  ```
- **URLs** (`dashboard/urls.py`):
  ```python
  from django.urls import path
  from .views import dashboard_view

  urlpatterns = [
      path('', dashboard_view, name='dashboard'),
  ]
  ```
- **Templates**:
  - `employer_dashboard.html`: Lists jobs posted and applications received, with logout button.
  - `seeker_dashboard.html`: Lists applications submitted, with logout button.
- **Outcome**:
  - Accessible at `/dashboard/`.
  - Employers see their jobs and applications; seekers see their applications.
  - Uses optimized queries with `select_related`.

### 5. Bootstrap Integration
- **Purpose**: Ensure a consistent, responsive UI.
- **Base Template** (`templates/base.html`):
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{% block title %}Smart Job Portal{% endblock %}</title>
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
      <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
  </head>
  <body>
      <div class="container">
          {% block content %}{% endblock %}
      </div>
  </body>
  </html>
  ```
- **Outcome**:
  - All templates extend `base.html` for consistent styling.
  - Bootstrap JavaScript enables form validation in `register.html`.
  - Responsive design with cards, forms, and pagination.

### 6. File Uploads (Resumes)
- **Purpose**: Enable seekers to upload resumes when applying for jobs.
- **Configuration** (`settings.py`):
  ```python
  import os
  MEDIA_URL = '/media/'
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  ```
- **URLs** (`smartjobportal/urls.py`):
  ```python
  from django.contrib import admin
  from django.urls import path, include
  from django.conf import settings
  from django.conf.urls.static import static

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('accounts/', include('accounts.urls')),
      path('dashboard/', include('dashboard.urls')),
      path('jobs/', include('jobs.urls')),
  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```
- **Outcome**:
  - Resumes stored in `media/resumes/`.
  - Served correctly in development.

## Key Configurations
- **Database**: SQLite (default).
- **Authentication**:
  - `AUTH_USER_MODEL = 'accounts.CustomUser'`
  - Redirects: `LOGIN_REDIRECT_URL = 'dashboard'`, `LOGOUT_REDIRECT_URL = 'login'`
- **Templates**: `TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'templates')]`
- **Sites Framework**: `SITE_ID = 1` for email verification.
- **Admin**: Models registered for `CustomUser`, `Job`, `Application`.

## Usage
- **Register**: `/accounts/register/` (choose Seeker/Employer, verify email).
- **Login**: `/accounts/login/`.
- **Logout**: `/accounts/logout/` or dashboard button.
- **Password Reset**: `/accounts/password_reset/`.
- **Browse Jobs**: `/jobs/` (published jobs, paginated).
- **Job Details**: `/jobs/<pk>/` (apply as seeker).
- **Manage Jobs**: `/jobs/create/`, `/jobs/<pk>/update/`, `/jobs/<pk>/delete/` (employers only).
- **Dashboard**: `/dashboard/` (employer: jobs/applications; seeker: applications).
- **Admin**: `/admin/` for management.

## Pending Tasks
- **Application Status**:
  - Dashboards reference `app.status`, but `Application` model lacks `status`. Suggested:
    ```python
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    ```
  - Run: `python manage.py makemigrations jobs; python manage.py migrate`
- **Unknown Role Template**:
  - `dashboard/unknown_role.html` needed for users without roles:
    ```html
    {% extends 'base.html' %}
    {% block content %}
    <div class="container mt-5">
        <h2>Error</h2>
        <p>Your account has no assigned role. Please contact support.</p>
    </div>
    {% endblock %}
    ```
- **Employer Dashboard**:
  - Uses `Job.objects` instead of `Job.active_jobs`. Update to show only published jobs if desired.

## Presentation Points
- **Modular Design**: Separated concerns into `accounts`, `jobs`, `dashboard`, `core` apps.
- **Custom User Model**: Supports Seeker/Employer roles with `is_seeker`/`is_employer` flags.
- **Authentication**: Full system with email verification, password reset, and Bootstrap-styled forms.
- **Job Management**: CBVs for CRUD operations, `ActiveJobManager` for published jobs, pagination.
- **Dashboards**: Role-specific views with optimized queries.
- **UI/UX**: Bootstrap for responsive design, client-side validation in registration.
- **File Uploads**: Resume uploads configured with `MEDIA_URL`/`MEDIA_ROOT`.
- **Future Work**: Add `status` field, `unknown_role.html`, job search, and application status management.