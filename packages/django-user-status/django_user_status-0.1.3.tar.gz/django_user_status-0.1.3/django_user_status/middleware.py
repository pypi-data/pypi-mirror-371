# middleware.py

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


class UserStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_duration = getattr(settings, "USER_STATUS_CACHE_DURATION", 300)
        self.cache_key_prefix = getattr(
            settings, "USER_STATUS_CACHE_KEY_PREFIX", "last_seen"
        )

    def __call__(self, request):
        if request.user.is_authenticated:
            cache.set(
                f"{self.cache_key_prefix}_{request.user.id}",
                timezone.now(),
                self.cache_duration,
            )
        response = self.get_response(request)
        return response
