from celery import shared_task
from django.contrib.auth import get_user_model
from core.emails import (
    send_activation_email, 
    send_welcome_email, 
    send_job_approval_email, 
    send_application_notification_email
)

@shared_task
def send_activation_email_task(user_id, domain):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    # الان domain باید استرینگ باشه، نه dict!
    send_activation_email(user, domain)

@shared_task
def send_welcome_email_task(user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    send_welcome_email(user)

@shared_task
def send_job_approval_email_task(job_id):
    from jobs.models import Job
    job = Job.objects.get(pk=job_id)
    send_job_approval_email(job)

@shared_task
def send_application_notification_email_task(application_id):
    from jobs.models import Application
    application = Application.objects.get(pk=application_id)
    send_application_notification_email(application)
