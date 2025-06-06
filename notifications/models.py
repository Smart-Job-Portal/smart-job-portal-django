from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional link to more info"
    )

    def __str__(self):
        # Improved: Shows username and keeps message clean
        name = getattr(self.user, "get_full_name", None)
        username = self.user.get_full_name() if name else str(self.user)
        msg = self.message.strip().replace("\n", " ")
        return f"Notification for {username}: {msg[:50]}{'...' if len(msg) > 50 else ''}"

    def mark_as_read(self, save=True):
        """Mark this notification as read. Optionally save immediately."""
        self.is_read = True
        if save:
            self.save(update_fields=["is_read"])

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"


    def as_dict(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read,
            "link": self.link,
        }


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    path = models.CharField(max_length=512)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} [{self.method}] {self.path} ({self.user})"
