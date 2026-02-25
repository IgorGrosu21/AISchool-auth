from django.db import models
from shared_backend.api.models import WithUUID

from .user import User


class LoginEvent(WithUUID):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_events", db_index=True
    )

    # Timestamps
    login_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Network info
    ip_address = models.GenericIPAddressField(null=False, db_index=True)
    country = models.CharField(  # noqa: DJ001
        max_length=2, null=True, blank=True, db_index=True
    )  # ISO 3166-1 alpha-2
    city = models.CharField(max_length=100, null=True, blank=True)  # noqa: DJ001
    isp = models.CharField(max_length=200, null=True, blank=True)  # noqa: DJ001

    # Device info
    user_agent = models.TextField(null=False)
    device_type = models.CharField(  # noqa: DJ001
        max_length=20, null=True, blank=True
    )  # mobile, desktop, tablet
    device_fingerprint = models.CharField(  # noqa: DJ001
        max_length=64, null=True, blank=True, db_index=True
    )  # Hash

    # Browser/OS
    browser = models.CharField(max_length=50, null=True, blank=True)  # noqa: DJ001
    browser_version = models.CharField(max_length=20, null=True, blank=True)  # noqa: DJ001
    os = models.CharField(max_length=50, null=True, blank=True)  # noqa: DJ001
    os_version = models.CharField(max_length=20, null=True, blank=True)  # noqa: DJ001

    # Application context
    login_method = models.CharField(max_length=20, null=False)  # password, google, facebook
    success = models.BooleanField(default=True, db_index=True)  # Track failed attempts too
    failure_reason = models.CharField(  # noqa: DJ001
        max_length=100, null=True, blank=True
    )  # password_incorrect, etc.

    # Additional metadata (JSON for flexibility)
    metadata = models.JSONField(
        null=True, blank=True
    )  # Screen resolution, timezone, language, etc.

    class Meta:
        verbose_name = "Событие входа"
        verbose_name_plural = "События входа"
        ordering = ["-login_at"]
