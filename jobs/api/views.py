from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from jobs.models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer

# Permissions
class IsEmployerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.employer == request.user

class IsJobSeeker(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'is_seeker', False)

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'is_employer', False)

# Job CRUD
class JobViewSet(ModelViewSet):
    queryset = Job.active_jobs.active()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEmployerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        salary = self.request.query_params.get('salary')
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if salary:
            queryset = queryset.filter(salary__icontains=salary)
        return queryset

# Apply to a job
class ApplyJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]
    throttle_scope = 'apply-job'

    def create(self, request, *args, **kwargs):
        job = get_object_or_404(Job, pk=self.kwargs['job_id'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(job=job, seeker=request.user, status='Pending')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Employer checks applications for a job
class JobApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get_queryset(self):
        job = get_object_or_404(Job, pk=self.kwargs['job_id'], employer=self.request.user)
        return Application.objects.filter(job=job)

# Accept / Reject endpoints
class ManageApplicationStatusView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    throttle_scope = 'manage-application'

    def update(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.kwargs['application_id'])
        if application.job.employer != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        new_status = self.kwargs['status']
        if new_status not in ['Accepted', 'Rejected']:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()
        serializer = self.get_serializer(application)
        return Response(serializer.data)
