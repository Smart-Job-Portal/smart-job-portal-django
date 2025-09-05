# notifications/utils.py
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

def notify_user(user, message, link=None, email_subject=None, email_body=None, html_message=None):
    Notification.objects.create(user=user, message=message, link=link)
    if email_subject and user.email:
        send_mail(
            subject=email_subject,
            message=email_body or message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message,    
        )

