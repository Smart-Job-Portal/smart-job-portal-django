from django.shortcuts import redirect

def check_user_role(strategy, backend, user, *args, **kwargs):
    request = strategy.request

    # User logged in but no role yet
    if not (user.is_employer or user.is_seeker):
        request.session['temp_social_login'] = True
        return redirect('choose_role')

def set_role_from_session(strategy, details, user=None, *args, **kwargs):
    if not user:
        return
    request = strategy.request
    pending_role = request.session.get('pending_role')
    if pending_role and not (user.is_employer or user.is_seeker):
        if pending_role == 'employer':
            user.is_employer = True
            user.is_seeker = False
        elif pending_role == 'seeker':
            user.is_seeker = True
            user.is_employer = False
        user.save()
    # Clean up session regardless
    request.session.pop('pending_role', None)