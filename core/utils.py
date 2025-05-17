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
    
    subject = "Your job listing has been approved"
    context = {
        'employer_name': job.employer.username,
        'job_title': job.title
    }
    message_plain = f"Dear {job.employer.username},\n\nYour job listing '{job.title}' has been approved and is now live on our platform."

    message_html = render_to_string('jobs/job_approval_email.html', context)

    send_mail(
        subject=subject,
        message=message_plain,
        from_email=None,
        recipient_list=[job.employer.email],
        html_message=message_html,
        fail_silently=True,
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

    send_mail(
        subject=subject,
        message=message_plain,
        from_email=None,  
        recipient_list=[application.job.employer.email],
        html_message=message_html,
        fail_silently=True,
    )
