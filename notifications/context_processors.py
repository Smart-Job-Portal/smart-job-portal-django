from .models import Notification

def user_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:10]  # latest 10
        return {'user_notifications': notifications}
    return {}
