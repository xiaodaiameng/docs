from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.sql import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)

async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def close_db():
    await test_engine.dispose()
