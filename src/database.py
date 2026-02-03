"""
Database Configuration - Project Kancil
Sets up the asynchronous SQLAlchemy engine, session factory, 
and declarative base for ORM models.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Importing the central config object
from src.config import config

# Initialize the Asynchronous Engine
# We set echo=False for production to avoid log clutter
engine = create_async_engine(config.DATABASE_URL, echo=False)

# Session factory for creating new database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

async def get_db():
    """
    Dependency generator for database sessions.
    Ensures that sessions are properly closed after use.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """
    Initializes the database schema.
    Creates all tables defined in the models if they do not exist.
    """
    async with engine.begin() as conn:
        # Note: In a production environment, consider using Alembic for migrations 
        # instead of create_all.
        await conn.run_sync(Base.metadata.create_all)