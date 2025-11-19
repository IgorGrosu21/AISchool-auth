from sqlalchemy.orm import Session

from ..database import with_commit
from ..models import User

def fetch_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

@with_commit(refresh=True)
def create_user(db: Session, email: str, password: str = None, is_verified: bool = False) -> User:
    user = User.create(email, password, is_verified)
    db.add(user)
    return user

@with_commit(refresh=True)
def verify_user(db: Session, user: User) -> User:
    _ = db # suppress unused variable warning

    if user.is_verified:
        return user

    user.is_verified = True
    return user

@with_commit(refresh=True)
def set_user_password(db: Session, user: User, password: str) -> User:
    _ = db # suppress unused variable warning

    user.set_password(password)
    return user