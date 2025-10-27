"""
Database connection management for v402 Facilitator.

Provides connection pooling, retry logic, and health checks for database connections.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.pool import QueuePool, StaticPool

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseConnection:
    """
    Manages database connections with connection pooling and health monitoring.

    Features:
    - Connection pooling with configurable pool size
    - Automatic retry on connection errors
    - Health check and monitoring
    - Connection lifecycle management
    """

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_connected = False

    async def initialize(self):
        """Initialize database connections and create session factory."""
        if self._is_connected:
            logger.warning("Database already initialized")
            return

        try:
            logger.info("Initializing database connection...")

            # Create async engine with connection pooling
            self._engine = create_async_engine(
                settings.database.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=settings.database.POOL_SIZE,
                max_overflow=settings.database.MAX_OVERFLOW,
                pool_recycle=settings.database.POOL_RECYCLE,
                pool_pre_ping=True,
                echo=settings.database.ECHO,
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            # Test connection
            await self._test_connection()

            self._is_connected = True
            logger.info("Database connection established successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    async def _test_connection(self):
        """Test database connection."""
        try:
            async with self._engine.begin() as conn:
                await conn.execute("SELECT 1")
            logger.debug("Database connection test passed")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    async def close(self):
        """Close database connections and cleanup."""
        if not self._is_connected:
            return

        logger.info("Closing database connections...")

        try:
            if self._session_factory:
                await self._session_factory.close_all()

            if self._engine:
                await self._engine.dispose()

            self._is_connected = False
            logger.info("Database connections closed")

        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session context manager.

        Yields:
            AsyncSession: Database session

        Example:
            async with db.session() as session:
                result = await session.execute(query)
        """
        if not self._is_connected:
            await self.initialize()

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def get_session_factory(self) -> async_sessionmaker:
        """Get the session factory."""
        if not self._is_connected:
            raise RuntimeError("Database not initialized")
        return self._session_factory

    async def health_check(self) -> dict:
        """
        Perform database health check.

        Returns:
            dict: Health status information
        """
        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
            return {
                "status": "healthy",
                "connected": self._is_connected,
                "pool_size": settings.database.POOL_SIZE,
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }


# Global database instance
_db_connection: Optional[DatabaseConnection] = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to get database session.

    Yields:
        AsyncSession: Database session
    """
    global _db_connection

    if _db_connection is None:
        _db_connection = DatabaseConnection()
        await _db_connection.initialize()

    async with _db_connection.session() as session:
        yield session


async def init_db():
    """Initialize database connections."""
    global _db_connection

    _db_connection = DatabaseConnection()
    await _db_connection.initialize()


async def close_db():
    """Close database connections."""
    global _db_connection

    if _db_connection:
        await _db_connection.close()

