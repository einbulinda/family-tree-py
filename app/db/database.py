from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker

from app.core.config import settings

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Check your .env file.")

engine = create_async_engine(settings.DATABASE_URL,echo=True, future = True)

async_session = async_sessionmaker(engine, autoflush=False, autocommit=False)

async def get_db():
    async with async_session() as session:
        yield session