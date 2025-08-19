# file: app/core/database.py
# The correct configuration for a local, asynchronous SQLite database.

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app import models

sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

engine = create_async_engine(
    sqlite_url, 
    echo=True, 
    future=True,
    pool_pre_ping=True,  # Helps detect disconnected connections
    pool_recycle=3600,   # Recycle connections every hour
)

# Use async_sessionmaker instead of sessionmaker
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            # Ensure session is properly closed
            await session.close()