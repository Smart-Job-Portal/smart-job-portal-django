from django.contrib import admin
from .models import ActivityLog
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "path", "method", "status_code", "ip_address")
    search_fields = ("user__username", "path", "ip_address")
    list_filter = ("method", "status_code", "user")
    ordering = ("-timestamp",)
