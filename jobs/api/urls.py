from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, ApplyJobView, JobApplicationsListView, ManageApplicationStatusView

router = DefaultRouter()
router.register(r'', JobViewSet, basename='jobs')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:job_id>/apply/', ApplyJobView.as_view(), name='api-apply-job'),
    path('<int:job_id>/applications/', JobApplicationsListView.as_view(), name='api-job-applications'),
    path('applications/<int:application_id>/<str:status>/', ManageApplicationStatusView.as_view(), name='api-manage-application'),
]
