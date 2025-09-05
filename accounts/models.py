from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os
from PIL import Image


class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_seeker = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# Upload Path Functions 
def profile_pic_upload_to(instance, filename):
    # Organized in: media/user_<id>/profile_pics/filename.jpg
    return f'user_{instance.user.id}/profile_pics/{filename}'

def resume_upload_to(instance, filename):
    # Organized in: media/user_<id>/resumes/filename.pdf
    return f'user_{instance.user.id}/resumes/{filename}'

#  User Profile Model 
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=profile_pic_upload_to, blank=True, null=True)
    image_thumbnail = models.ImageField(upload_to=profile_pic_upload_to, editable=False, blank=True, null=True)
    resume = models.FileField(upload_to=resume_upload_to, blank=True, null=True)
    bio = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image and hasattr(self.image, 'path'):
            thumb_size = (150, 150)
            with Image.open(self.image.path) as im:
                im = im.convert('RGB')
                im.thumbnail(thumb_size)

                # Thumbnail name and path
                thumb_filename = f"thumb_{os.path.basename(self.image.name)}"
                thumb_dir = os.path.dirname(self.image.path)
                thumb_path = os.path.join(thumb_dir, thumb_filename)
                im.save(thumb_path, "JPEG")

                # Save thumbnail relative path into model field
                rel_thumb_path = os.path.join(
                    os.path.dirname(self.image.name),
                    thumb_filename
                )
                if self.image_thumbnail != rel_thumb_path:
                    self.image_thumbnail = rel_thumb_path
                    # Save without infinite recursion
                    models.Model.save(self, update_fields=['image_thumbnail'])

    def __str__(self):
        return f"{self.user.username} Profile"
