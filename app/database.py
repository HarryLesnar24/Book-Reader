from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from .config import Config


asyncEngine = create_async_engine(Config.DATABASE_URL)


async def getSession() -> AsyncGenerator[AsyncSession, None]:
    Session = async_sessionmaker(
        bind=asyncEngine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session
