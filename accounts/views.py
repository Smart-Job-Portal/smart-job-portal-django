from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile
from .tokens import account_activation_token
from core.tasks import send_activation_email_task, send_welcome_email_task
from core.utils import send_welcome_email
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes



from django.shortcuts import redirect

def set_role_and_social_redirect(request, role):
    if role in ['employer', 'seeker']:
        request.session['pending_role'] = role
    return redirect('social:begin', 'google-oauth2')


# ------------------ Registration View ------------------


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES if request.FILES else None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            # Build absolute URL and force https scheme
            activate_url = request.build_absolute_uri(
    reverse('activate', args=[uid, token])
).replace("http://", "https://")

          

            # Pass activate_url to the async task
            send_activation_email_task.delay(user.id, activate_url)

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
        login(
            request,
            user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

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

# ------------------ Profile View ------------------
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

# ------------------ Profile Edit View ------------------
@login_required
def profile_edit_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            # ----------- NO NAMESPACE: only 'profile', not 'accounts:profile'
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})
