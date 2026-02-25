from datetime import datetime
from typing import TYPE_CHECKING, Optional

from django.db import models
from shared_backend.api.models import WithUUID

from .login_event import LoginEvent
from .user import User

if TYPE_CHECKING:
    from .refresh_token import RefreshToken


class Chain(WithUUID):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chains", db_index=True)
    login_event = models.OneToOneField(
        LoginEvent, on_delete=models.CASCADE, related_name="chain", db_index=True
    )
    remember_me = models.BooleanField(default=False)

    tokens: models.Manager["RefreshToken"]

    def __len__(self) -> int:
        return self.tokens.count()

    def active_token(self) -> Optional["RefreshToken"]:
        return self.tokens.filter(is_revoked=False).order_by("-created_at").first()

    def root_token(self) -> Optional["RefreshToken"]:
        """Get the first token in the chain (oldest by creation time)"""
        return self.tokens.order_by("created_at").first()

    def revoke(self) -> None:
        self.tokens.update(is_revoked=True)

    def delete_tokens(self, expiration_time: datetime | None = None) -> None:
        if expiration_time is None:
            self.delete()
            return

        self.tokens.filter(expires_at__lte=expiration_time).delete()

    def __str__(self) -> str:
        return f"{self.user.email} - {self.login_event.id}"

    class Meta:
        verbose_name = "Цепочка токенов"
        verbose_name_plural = "Цепочки токенов"
        ordering = ["user__id"]
