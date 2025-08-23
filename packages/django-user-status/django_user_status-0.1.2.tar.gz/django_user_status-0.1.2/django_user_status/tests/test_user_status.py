from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from django_user_status.middleware import UserStatusMiddleware
from django_user_status.templatetags import user_status_tags


class UserStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.factory = RequestFactory()

    def tearDown(self):
        cache.clear()

    def test_middleware_updates_cache(self):
        request = self.factory.get("/")
        request.user = self.user

        middleware = UserStatusMiddleware(lambda req: None)
        middleware(request)

        last_seen = cache.get(f"{settings.USER_STATUS_CACHE_KEY_PREFIX}_{self.user.id}")
        self.assertIsNotNone(last_seen)
        self.assertTrue(timezone.is_aware(last_seen))

    def test_online_status(self):
        cache.set(
            f"{settings.USER_STATUS_CACHE_KEY_PREFIX}_{self.user.id}",
            timezone.now(),
            settings.USER_STATUS_CACHE_DURATION,
        )

        status = user_status_tags.get_user_status(self.user)
        self.assertEqual(status, "online")

    def test_offline_status(self):
        old_time = timezone.now() - timedelta(
            seconds=settings.USER_STATUS_CACHE_DURATION + 1
        )
        cache.set(
            f"{settings.USER_STATUS_CACHE_KEY_PREFIX}_{self.user.id}",
            old_time,
            settings.USER_STATUS_CACHE_DURATION,
        )

        status = user_status_tags.get_user_status(self.user)
        self.assertEqual(status, "offline")

    def test_last_seen_tag(self):
        test_time = timezone.now()
        cache.set(f"{settings.USER_STATUS_CACHE_KEY_PREFIX}_{self.user.id}", test_time)

        last_seen = user_status_tags.get_last_seen(self.user)
        self.assertEqual(last_seen, test_time)
