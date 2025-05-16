from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_welcome_email(user):
    subject = 'Welcome to Smart Job Portal!'
    message = render_to_string('accounts/welcome_email.html', {'user': user})
    send_mail(
        subject=subject,
        message='Welcome to Smart Job Portal! Your account has been activated.',
        from_email=None,
        recipient_list=[user.email],
        html_message=message,
        fail_silently=True,
    )


def send_job_approval_email(job):
    """
    Sends an email notification to the employer when their job is approved.
    """
    subject = "Your job listing has been approved"
    context = {
        'employer_name': job.employer.username,
        'job_title': job.title
    }
    message_plain = f"Dear {job.employer.username},\n\nYour job listing '{job.title}' has been approved and is now live on our platform."

    # Optionally, if you use an HTML template for the email:
    message_html = render_to_string('jobs/job_approval_email.html', context)

    send_mail(
        subject=subject,
        message=message_plain,
        from_email=None,  # Replace this with your email address
        recipient_list=[job.employer.email],
        html_message=message_html,
        fail_silently=True,
    )
