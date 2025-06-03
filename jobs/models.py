from django.db import models
from django.conf import settings
from django.dispatch import receiver
from core.utils import send_application_notification_email 
from core.utils import send_job_approval_email
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

class ActiveJobManager(models.Manager):
    def active(self):
        
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
    published = models.BooleanField(default=False)  

    objects = models.Manager()  
    active_jobs = ActiveJobManager()  

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
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seeker.username} applied for {self.job.title}"
    

@receiver(post_save, sender=Application)
def notify_employer_on_application(sender, instance, created, **kwargs):
    
    if created and instance.status == "Pending":
        send_application_notification_email(instance)
        #send_application_notification_email_task.delay(application.id)


@receiver(pre_save, sender=Job)
def set_published_flag(sender, instance, **kwargs):
    if not instance.pk:
        instance._published_was = False
    else:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._published_was = old.published
        except sender.DoesNotExist:
            instance._published_was = False

@receiver(post_save, sender=Job)
def job_published_email_signal(sender, instance, created, **kwargs):
    if not created and hasattr(instance, "_published_was"):
        if not instance._published_was and instance.published:
            send_job_approval_email(instance)
            #send_job_approval_email_task.delay(job.id)
