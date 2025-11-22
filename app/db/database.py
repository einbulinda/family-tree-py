from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Check your .env file.")

engine = create_engine(settings.DATABASE_URL,echo=True, future = True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy Session
    and makes sure it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
