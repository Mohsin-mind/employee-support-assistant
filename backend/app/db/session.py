import time
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.core.logging import logger

# Create async engine with connection pooling
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rollback due to exception: {e}")
            raise
        finally:
            await session.close()


async def check_database_connection() -> dict:
    """Check database health by running SELECT 1 and computing latency."""
    start_time = time.perf_counter()
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        _ = result.scalar()
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return {
        "status": "connected",
        "database": settings.DB_DATABASE,
        "host": settings.DB_HOST_NAME,
        "latency_ms": latency_ms,
    }
