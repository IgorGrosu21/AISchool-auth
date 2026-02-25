import secrets
import string

from django.db import models
from shared_backend.api.models import WithUUID

from api.models import User


class VerificationCode(WithUUID):
    PURPOSES = {
        "RESTORE_PASSWORD": "restore_password",
        "VERIFY_EMAIL": "verify_email",
        "VERIFY_BACKUP_EMAIL": "verify_backup_email",
    }

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_codes", default=None
    )
    purpose = models.CharField(max_length=19, choices=PURPOSES)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Проверочный код"
        verbose_name_plural = "Проверочные коды"
        ordering = ["-created_at"]

    @classmethod
    def _generate_code(cls, length: int = 6) -> str:
        """Generate a verification code consisting of digits and uppercase letters"""
        alphabet = string.digits + string.ascii_uppercase
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @classmethod
    def create(cls, user: User, purpose: str) -> "VerificationCode":
        """Create a verification code"""
        code = cls._generate_code()
        return cls(user=user, purpose=purpose, code=code)
