from django.contrib.auth.decorators import login_required
from jobs.models import Job, Application  
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def dashboard_view(request):
    user = request.user

    if hasattr(user, 'is_employer') and user.is_employer:
        
        jobs = Job.active_jobs.active().filter(employer=user)
        applications = Application.objects.filter(job__employer=user).select_related('job', 'seeker')  
        context = {
            'jobs': jobs,
            'applications': applications,
        }
        return render(request, 'dashboard/employer_dashboard.html', context)

    elif hasattr(user, 'is_seeker') and user.is_seeker:
        
        applications = Application.objects.filter(seeker=user).select_related('job') 
        context = {
            'applications': applications,
        }
        return render(request, 'dashboard/seeker_dashboard.html', context)
    else:
        
        return render(request, 'dashboard/unknown_role.html')
    

from django.contrib.auth.decorators import login_required

@login_required
def choose_role_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        user = request.user

        if role == 'employer':
            user.is_employer = True
            user.is_seeker = False
            user.save()
        elif role == 'seeker':
            user.is_seeker = True
            user.is_employer = False
            user.save()
        else:
            return render(request, 'dashboard/choose_role.html', {
                'error': 'Please select a valid role.'
            })

        # Clear temp_social_login after assigning role
        request.session.pop('temp_social_login', None)
        return redirect('dashboard')

    return render(request, 'dashboard/choose_role.html')
