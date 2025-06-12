from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from core.utils import send_welcome_email
from core.tasks import send_activation_email_task, send_welcome_email_task

from django.contrib.auth.views import PasswordResetView
from django.contrib import messages

# ------------------ Registration View ------------------
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES if request.FILES else None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            domain = get_current_site(request).domain
            send_activation_email_task.delay(user.id, domain)

            messages.info(request, "Please check your email to activate your account before logging in.")
            return render(request, 'accounts/please_check_email.html')
        else:
            messages.error(request, "There was a problem with your registration. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# ------------------ Account Activation View ------------------
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)

        send_welcome_email_task.delay(user.id)
        try:
            send_welcome_email(user)
        except Exception:
            pass

        messages.success(request, "Your account has been activated! You are now logged in.")
        return redirect('dashboard')
    else:
        messages.error(request, "Activation link is invalid or has expired. Please register again or contact support if you need help.")
        return redirect('login')

# ============================================================
#         ADD YOUR PROFILE VIEW FUNCTION HERE!
# ============================================================

from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def profile_view(request):
    # Defensive: always ensure a profile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

from .forms import UserProfile

from .forms import CustomUserCreationForm, UserProfileForm

@login_required
def profile_edit_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})


