from django.urls import path
from .views import JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView, apply_job, job_applications , accept_application ,reject_application

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('create/', JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/update/', JobUpdateView.as_view(), name='job_update'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
    path('<int:job_id>/apply/', apply_job, name='apply_job'),
    path('<int:job_id>/applications/', job_applications, name='job_applications'),
    path('applications/<int:application_id>/accept/', accept_application, name='accept_application'),
    path('applications/<int:application_id>/reject/', reject_application, name='reject_application'),
]
