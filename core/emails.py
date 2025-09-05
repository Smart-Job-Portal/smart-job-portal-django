from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from accounts.tokens import account_activation_token
from notifications.utils import notify_user
from django.contrib.auth import get_user_model

def send_activation_email(user_id, activate_url):
    
    User = get_user_model()
    user = User.objects.get(pk=user_id)

    subject = 'Activate your Smart Job Portal account'
    context = {
        'user': user,
        'activate_url': activate_url,
    }

  
    html_message = render_to_string('accounts/activation_email.html', context)
    plain_message = f"Hi {user.username},\n\nPlease activate your account by clicking the following link:\n{activate_url}\n\nThanks!"

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_welcome_email(user):
    subject = 'Welcome to Smart Job Portal!'
    html_message = render_to_string('accounts/welcome_email.html', {'user': user})
    notify_user(
        user=user,
        message="Welcome to Smart Job Portal! Your account has been activated.",
        link="/dashboard/",
        email_subject=subject,
        email_body="Welcome to Smart Job Portal! Your account has been activated.",
        html_message=html_message,
    )

def send_job_approval_email(job):
    subject = "Your job listing has been approved"
    context = {
        'employer_name': job.employer.username,
        'job_title': job.title
    }
    message_plain = f"Dear {job.employer.username},\n\nYour job listing '{job.title}' has been approved and is now live on our platform."
    message_html = render_to_string('jobs/job_approval_email.html', context)

    notify_user(
        user=job.employer,
        message=f"Your job listing '{job.title}' has been approved!",
        link=f"/jobs/{job.id}/",
        email_subject=subject,
        email_body=message_plain,
        html_message=message_html,
    )

def send_application_notification_email(application):
    subject = "Someone applied to your job!"
    context = {
        'employer_name': application.job.employer.username,
        'job_title': application.job.title,
        'seeker_name': application.seeker.username,
        'seeker_email': application.seeker.email,
    }
    message_plain = (
        f"Dear {application.job.employer.username},\n\n"
        f"{application.seeker.username} has applied for your job '{application.job.title}'.\n"
        "Best regards,\nYour Website Team"
    )
    message_html = render_to_string('jobs/new_application_email.html', context)

    notify_user(
        user=application.job.employer,
        message=f"{application.seeker.username} applied for your job '{application.job.title}'.",
        link=f"/jobs/{application.job.id}/applications/",
        email_subject=subject,
        email_body=message_plain,
        html_message=message_html,
    )
