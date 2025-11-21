from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL,echo=True)

async_session = async_sessionmaker(engine, autoflush=False, autocommit=False)

async def get_db():
    async with async_session() as session:
        yield session