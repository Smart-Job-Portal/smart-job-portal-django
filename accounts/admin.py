from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,UserProfile

admin.site.register(CustomUser, UserAdmin)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'image_tag', 'resume')
    readonly_fields = ("image_thumbnail", )

    def image_tag(self, obj):
        if obj.image_thumbnail:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="height:50px;width:50px;border-radius:4px;object-fit:cover;">', obj.image_thumbnail.url)
        return "-"
    image_tag.short_description = "Thumbnail"