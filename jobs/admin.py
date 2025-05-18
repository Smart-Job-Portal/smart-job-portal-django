from django.contrib import admin

from core.utils import send_job_approval_email
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'posted_on', 'published')
    list_filter = ('published', 'posted_on')  
    search_fields = ('title', 'description')  

    actions = ['approve_jobs']

def approve_jobs(self, request, queryset):
        
        for job in queryset:
            if not job.published:  
                job.published = True
                job.save()

                send_job_approval_email(job)

        self.message_user(request, f"{queryset.count()} job(s) successfully approved.")

approve_jobs.short_description = "Mark selected jobs as published"

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'seeker', 'applied_on', 'status')  
    list_filter = ('status', 'applied_on')