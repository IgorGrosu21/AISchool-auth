from datetime import datetime
import secrets
import string
from typing import Optional, Type

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from .database import Base

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to refresh tokens
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    # Relationship to verification codes
    verification_codes = relationship("VerificationCode", back_populates="user", cascade="all, delete-orphan")

    def has_password(self) -> bool:
        """Check if user has a password"""
        return self.password_hash is not None

    def set_password(self, password: Optional[str]):
        """Set password hash or clear it when None"""
        if password is None:
            self.password_hash = None
            return

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches"""
        if not self.has_password():
            return False

        return check_password_hash(self.password_hash, password)

    @classmethod
    def create(cls: Type["User"], email: str, password: str = None, is_verified: bool = False) -> "User":
        """Create a new user"""
        user = cls(email=email, is_verified=is_verified)
        user.set_password(password)
        return user


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)  # JWT ID (token identifier)
    user_email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_blacklisted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to user
    user = relationship("User", back_populates="refresh_tokens")

    def blacklist(self):
        """Blacklist the refresh token"""
        self.is_blacklisted = True

    @classmethod
    def create(
        cls: Type["RefreshToken"],
        jti: str,
        user_email: str,
        expires_at: datetime,
        is_blacklisted: bool = False,
    ) -> "RefreshToken":
        """Create a new refresh token record"""
        return cls(
            jti=jti,
            user_email=user_email,
            expires_at=expires_at,
            is_blacklisted=is_blacklisted,
        )

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(String, nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship to user
    user = relationship("User", back_populates="verification_codes")

    @classmethod
    def _generate_code(cls: Type["VerificationCode"], length: int = 6) -> str:
        """Generate a verification code consisting of digits and uppercase letters"""
        alphabet = string.digits + string.ascii_uppercase
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @classmethod
    def create(cls: Type["VerificationCode"], email: str, purpose: str) -> "VerificationCode":
        """Create a verification code"""
        code = cls._generate_code()
        return cls(email=email, purpose=purpose, code=code)