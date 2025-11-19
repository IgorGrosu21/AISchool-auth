from sqlalchemy.orm import Session

from ..database import with_commit
from ..models import VerificationCode

def fetch_verification_code(db: Session, email: str, purpose: str, code: str) -> VerificationCode:
    return db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.purpose == purpose,
        VerificationCode.code == code
    ).order_by(VerificationCode.created_at.desc()).first()

@with_commit(refresh=False)
def delete_verification_codes(db: Session, email: str, purpose: str) -> None:
    _ = db # suppress unused variable warning

    db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.purpose == purpose,
    ).delete(synchronize_session=False)

@with_commit(refresh=True)
def create_verification_code(db: Session, email: str, purpose: str) -> VerificationCode:
    code = VerificationCode.create(email, purpose)
    db.add(code)
    return code