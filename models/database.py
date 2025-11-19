from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, sessionmaker

from core import DATABASE_URL

# Configure engine based on database type
# SQLite needs check_same_thread=False, PostgreSQL doesn't
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def with_commit(refresh: bool = True):
    """Decorator that commits the database and refreshes the result if needed"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            db: Session = args[0]
            db.commit()
            if refresh and result:
                db.refresh(result)
            return result
        return wrapper
    return decorator