"""
Database-backed token blacklist for refresh tokens.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.models import RefreshToken


class TokenBlacklist:
    """Token blacklist using database storage"""
    
    def add(self, db: Session, token: str, expires_at: datetime, user_email: str, jti: str = None):
        """Add token to blacklist or create token record"""
        # Try to find existing token by jti or token string
        if jti:
            existing_token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
        else:
            existing_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        
        if existing_token:
            # Update existing token to blacklisted
            existing_token.is_blacklisted = True
        else:
            # Create new token record
            new_token = RefreshToken(
                jti=jti or self._generate_jti_from_token(token),
                user_email=user_email,
                token=token,
                expires_at=expires_at,
                is_blacklisted=True
            )
            db.add(new_token)
        
        db.commit()
    
    def is_blacklisted(self, db: Session, token: str, jti: str = None) -> bool:
        """Check if token is blacklisted"""
        # Clean expired tokens first
        self._clean_expired_tokens(db)
        
        # Check if token is blacklisted
        if jti:
            token_record = db.query(RefreshToken).filter(
                RefreshToken.jti == jti,
                RefreshToken.is_blacklisted == True
            ).first()
        else:
            token_record = db.query(RefreshToken).filter(
                RefreshToken.token == token,
                RefreshToken.is_blacklisted == True
            ).first()
        
        return token_record is not None
    
    def clear_user_tokens(self, db: Session, user_email: str):
        """Blacklist all tokens for a user (logout-all functionality)"""
        # Mark all user's tokens as blacklisted
        db.query(RefreshToken).filter(
            RefreshToken.user_email == user_email,
            RefreshToken.is_blacklisted == False
        ).update({"is_blacklisted": True})
        
        db.commit()
    
    def create_token_record(self, db: Session, token: str, user_email: str, expires_at: datetime, jti: str = None):
        """Create a new token record (not blacklisted)"""
        # Generate jti if not provided
        if not jti:
            jti = self._generate_jti_from_token(token)
        
        # Check if token already exists
        existing = db.query(RefreshToken).filter(
            or_(RefreshToken.jti == jti, RefreshToken.token == token)
        ).first()
        
        if existing:
            # Update existing record
            existing.token = token
            existing.expires_at = expires_at
            existing.is_blacklisted = False
            existing.user_email = user_email
        else:
            # Create new record
            new_token = RefreshToken(
                jti=jti,
                user_email=user_email,
                token=token,
                expires_at=expires_at,
                is_blacklisted=False
            )
            db.add(new_token)
        
        db.commit()
        return jti
    
    def _clean_expired_tokens(self, db: Session):
        """Remove expired tokens from database"""
        now = datetime.now(timezone.utc)
        db.query(RefreshToken).filter(RefreshToken.expires_at < now).delete()
        db.commit()
    
    def _generate_jti_from_token(self, token: str) -> str:
        """Generate a JTI (JWT ID) from token string"""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()[:32]


# Global token blacklist instance
token_blacklist = TokenBlacklist()
