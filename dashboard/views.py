from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    if request.user.is_employer:
        return render(request, 'dashboard/employer_dashboard.html')
    elif request.user.is_seeker:
        return render(request, 'dashboard/seeker_dashboard.html')
    else:
        return render(request, 'dashboard/unknown_role.html')