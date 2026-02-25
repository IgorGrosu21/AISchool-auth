from django.db import models
from django.utils import timezone

from .chain import Chain


class RefreshToken(models.Model):
    jti = models.CharField(max_length=255, primary_key=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    # Chain tracking
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, related_name="tokens", db_index=True)

    # Status flags
    is_revoked = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Токен обновления"
        verbose_name_plural = "Токены обновления"
        ordering = ["chain__id", "-created_at"]

    def __str__(self) -> str:
        return f"{self.jti} - {self.chain.user.email}"

    def revoke(self) -> None:
        """Revoke the refresh token (automatic security revocation)"""
        self.is_revoked = True
        self.save()

    def is_expired(self) -> bool:
        return self.expires_at < timezone.now()
