from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from shared_backend.api.models import AuthenticateableUser


class User(AuthenticateableUser):
    email = models.EmailField(unique=True, db_index=True)
    backup_email = models.EmailField(blank=True, null=True, db_index=True)  # noqa: DJ001
    password_hash = models.CharField(max_length=255, null=True, blank=True)  # noqa: DJ001
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.email

    def has_password(self) -> bool:
        """Check if user has a password"""
        return self.password_hash is not None

    def set_password(self, password: str | None = None) -> None:
        """Set password hash or clear it when None"""
        if password is None:
            self.password_hash = None
            return
        self.password_hash = make_password(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches"""
        if not self.has_password():
            return False
        return check_password(password, self.password_hash)  # type: ignore
