from django.shortcuts import render, redirect
from django.contrib.auth import  login
from .forms import CustomUserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from core.utils import send_welcome_email

from core.tasks import send_activation_email_task, send_welcome_email_task

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()

            domain = get_current_site(request).domain
            send_activation_email_task.delay(user.id, {'domain': domain})

            return render(request, 'accounts/please_check_email.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


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


        send_welcome_email_task.delay(user.id)
        send_welcome_email(user)

        return redirect('dashboard')
    else:
        return HttpResponse('Activation link is invalid!')