from typing import AsyncGenerator

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core import settings

from .models import Base


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        *,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.url = make_url(url)
        self.engine = create_async_engine(
            url,
            **self._engine_kwargs(
                echo=echo,
                pool_size=pool_size,
                max_overflow=max_overflow,
            ),
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def _engine_kwargs(
        self,
        *,
        echo: bool,
        pool_size: int,
        max_overflow: int,
    ) -> dict:
        # SQLite
        if self.url.drivername.startswith("sqlite"):
            return {
                "echo": echo,
                "connect_args": {"check_same_thread": False},
            }

        # PostgreSQL / MySQL
        return {
            "echo": echo,
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_pre_ping": True,
        }

    async def init_db(self, *, drop: bool = False):
        async with self.engine.begin() as conn:
            if drop:
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def dispose(self):
        await self.engine.dispose()


db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
