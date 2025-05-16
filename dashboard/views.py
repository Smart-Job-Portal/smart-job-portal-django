from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Application  # Import from jobs app

@login_required
def dashboard_view(request):
    user = request.user

    if hasattr(user, 'is_employer') and user.is_employer:
        # Employer: Show jobs they posted and applications to those jobs
        jobs = Job.objects.filter(employer=user)
        applications = Application.objects.filter(job__employer=user).select_related('job', 'seeker')  # Optimize query
        context = {
            'jobs': jobs,
            'applications': applications,
        }
        return render(request, 'dashboard/employer_dashboard.html', context)

    elif hasattr(user, 'is_seeker') and user.is_seeker:
        # Seeker: Show jobs they applied for
        applications = Application.objects.filter(seeker=user).select_related('job') # Optimize query
        context = {
            'applications': applications,
        }
        return render(request, 'dashboard/seeker_dashboard.html', context)
    else:
        # Handle users with no roles
        return render(request, 'dashboard/unknown_role.html')