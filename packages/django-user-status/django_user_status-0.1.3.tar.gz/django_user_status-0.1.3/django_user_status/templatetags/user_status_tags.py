from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime

register = template.Library()


@register.simple_tag
def get_user_status(user):
    """
    Returns the user's status (online or offline) based on settings.
    """
    cache_duration = getattr(settings, "USER_STATUS_CACHE_DURATION", 300)
    cache_key_prefix = getattr(settings, "USER_STATUS_CACHE_KEY_PREFIX", "last_seen")

    last_seen_timestamp = cache.get(f"{cache_key_prefix}_{user.id}")
    if (
        last_seen_timestamp
        and (timezone.now() - last_seen_timestamp).total_seconds() < cache_duration
    ):
        return "online"
    return "offline"


@register.simple_tag
def get_last_seen(user):
    """
    Returns the user's last seen time.
    """
    cache_key_prefix = getattr(settings, "USER_STATUS_CACHE_KEY_PREFIX", "last_seen")

    last_seen_timestamp = cache.get(f"{cache_key_prefix}_{user.id}")
    if last_seen_timestamp:
        return last_seen_timestamp
    return None
