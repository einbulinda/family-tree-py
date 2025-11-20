from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://","postgresql=asyncpg://"),
    echo=True,
   )

AsyncSessionLocal = sessionmaker(
    bind=engine,class_=AsyncSession, expire_on_commit=False
)


# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session