# notifications/logging_middleware.py
from .models import ActivityLog

EXCLUDED_PATH_PREFIXES = (
    '/admin/', '/static/', '/media/', '/favicon.ico', '/__debug__/'
)

class ActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path

        if any(path.startswith(prefix) for prefix in EXCLUDED_PATH_PREFIXES):
            return response

        # Try to get the user's IP address
        ip = self._get_ip(request)

        ActivityLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            path=path,
            method=request.method,
            status_code=response.status_code,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            
            description=getattr(request, "_activity_description", "")
        )

        return response

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
