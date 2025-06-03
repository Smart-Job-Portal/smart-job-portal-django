from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Application  

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