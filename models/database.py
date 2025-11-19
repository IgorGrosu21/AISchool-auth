"""Database utilities"""

from functools import wraps
from flask import g

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

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session from Flask g"""
    if 'db' not in g:
        g.db = SESSION_LOCAL()
    return g.db

def close_db(_=None):
    """Close database session"""
    db = g.pop('db', None)
    if db is not None:
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
            # Get db from args or kwargs
            db = None
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            if not db and 'db' in kwargs:
                db = kwargs['db']
            if not db:
                db = get_db()

            db.commit()
            if refresh and result:
                db.refresh(result)
            return result
        return wrapper
    return decorator
