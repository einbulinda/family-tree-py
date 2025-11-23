import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


logger = logging.getLogger("family_tree.database")

if not settings.DATABASE_URL:
    logger.error("DATABASE_URL is missing in .env file!")
    raise ValueError("DATABASE_URL is missing!")

logger.info(f"Connecting to database: {settings.DATABASE_URL}")


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
    logger.debug("DB session opened")
    try:
        yield db
    finally:
        logger.debug("DB session closed")
        db.close()
