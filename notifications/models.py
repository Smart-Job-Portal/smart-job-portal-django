from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True, help_text="Optional link to more info")


    def __str__(self):
        return f"{self.user} - {self.message[:40]}{'...' if len(self.message) > 40 else ''}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    class Meta:
        ordering = ['-created_at']

