from django.contrib import admin

from core.utils import send_job_approval_email
from .models import Job, Application
from django.core.mail import send_mail


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'posted_on', 'published')
    list_filter = ('published', 'posted_on')  # Filters by moderation status and date
    search_fields = ('title', 'description')  # Adds search functionality

    actions = ['approve_jobs']

 


def approve_jobs(self, request, queryset):
        """Admin action to approve selected jobs and notify employers."""
        for job in queryset:
            if not job.published:  # Approve only unpublished jobs
                job.published = True
                job.save()

                # Send email to the employer
                send_job_approval_email(job)

        self.message_user(request, f"{queryset.count()} job(s) successfully approved.")

approve_jobs.short_description = "Mark selected jobs as published"

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'seeker', 'applied_on', 'status')  # Show status column
    list_filter = ('status', 'applied_on')
    actions = ['publish_applications']

    def publish_applications(self, request, queryset):
        """Admin action to mark selected applications as Published."""
        for application in queryset:
            if application.status == 'Pending':  # Publish only Pending applications
                application.status = 'Published'
                application.save()

                # Notify employer about published applications
                employer_email = application.job.employer.email
                send_mail(
                    subject="New Application Published",
                    message=(
                        f"The application from {application.seeker.username} "
                        f"for your job '{application.job.title}' has been published."
                    ),
                    from_email="noreply@yourdomain.com",
                    recipient_list=[employer_email],
                )

        self.message_user(request, f"{queryset.count()} application(s) published.")
    publish_applications.short_description = "Mark selected applications as Published"