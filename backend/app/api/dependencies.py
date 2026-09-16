from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that injects an async database session into route handlers."""
    async for session in get_async_session():
        yield session
