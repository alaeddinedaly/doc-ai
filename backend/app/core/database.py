"""Database configuration and session utilities."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide a database session for FastAPI dependencies."""

    async with SessionLocal() as session:
        yield session


async def init_models() -> None:
    """Create database tables if they do not exist."""

    from ..models import Base  # local import to avoid circular dependency

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

