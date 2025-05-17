from django.db import models
from django.conf import settings




class ActiveJobManager(models.Manager):
    def active(self):
        """Returns only published (admin-approved) jobs."""
        return super().get_queryset().filter(published=True)



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
     
    STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
]

     
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # Resume upload
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # Status field
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seeker.username} applied for {self.job.title}"
