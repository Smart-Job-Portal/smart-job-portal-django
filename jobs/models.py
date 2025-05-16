from django.db import models
from django.conf import settings

class ActiveJobManager(models.Manager):
    
    def get_queryset(self):
        """Retrieve jobs posted by a specific employer"""
        employer_username = self.request.GET.get('employer', None)  # Assume employer filter passed as a query parameter
        if employer_username:
            queryset = Job.objects.filter(employer__username=employer_username)
        else:
            queryset = Job.objects.all()
        print("Jobs in queryset:", list(queryset))  # Debugging output
        return queryset


class Job(models.Model):
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    posted_on = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)  # ADD THIS LINE

    objects = models.Manager()  # Default manager
    active_jobs = ActiveJobManager()  # Custom manager

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    resume = models.FileField(upload_to='resumes/')
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seeker.username} applied for {self.job.title}"
