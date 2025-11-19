from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..database import with_commit
from ..models import RefreshToken


def _ensure_datetime(value) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    # Assume UNIX timestamp (seconds)
    return datetime.fromtimestamp(value, tz=timezone.utc)


@with_commit(refresh=False)
def blacklist_refresh_tokens(db: Session, email: str) -> None:
    db.query(RefreshToken).filter(RefreshToken.user_email == email).update(
        {"is_blacklisted": True},
        synchronize_session=False,
    )


@with_commit(refresh=False)
def is_blacklisted(db: Session, jti: str) -> bool:
    # Clean expired tokens first
    now = datetime.now(timezone.utc)
    db.query(RefreshToken).filter(RefreshToken.expires_at < now).delete(synchronize_session=False)

    return db.query(RefreshToken).filter(
        RefreshToken.jti == jti,
        RefreshToken.is_blacklisted.is_(True)
    ).first() is not None


@with_commit(refresh=True)
def create_or_update_refresh_token(db: Session, payload: dict) -> RefreshToken:
    jti = payload["jti"]
    token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

    expires_at = _ensure_datetime(payload["expires_at"])

    if token:
        token.expires_at = expires_at
        token.is_blacklisted = payload.get("is_blacklisted", False)
        token.user_email = payload["user_email"]
    else:
        token = RefreshToken.create(
            jti=jti,
            user_email=payload["user_email"],
            expires_at=expires_at,
            is_blacklisted=payload.get("is_blacklisted", False),
        )
        db.add(token)

    return token