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