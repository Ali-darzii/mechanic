from typing import Any, AsyncGenerator, Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import setting

_async_engine = create_async_engine(setting.POSTGRES_URL, echo=setting.DEBUG, future=True)
_AsyncSessionLocal = sessionmaker(bind=_async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_postdb() -> AsyncGenerator[AsyncSession, None]:
    """
    Async session dependency for FastAPI.
    Use with Depends(get_postdb)
    """
    async with _AsyncSessionLocal() as session:
        yield session


_engine = create_engine(setting.POSTGRES_URL.replace("asyncpg","psycopg2"))
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

@contextmanager
def get_postdb_cm() -> Generator[Any, Any, None]:
    """ sync context manager for scripts or backgroung tasks. """
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
