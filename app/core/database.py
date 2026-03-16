"""
app/core/database.py
────────────────────
Creates the SQLAlchemy async engine and session factory.
Use `get_db()` as a FastAPI dependency to get a database session.

Example usage in a route:
    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        ...
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# Create the async engine.
# pool_pre_ping=True tests the connection before using it — prevents
# "connection closed" errors after the DB has been idle.
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,       # max persistent connections
    max_overflow=20,    # extra connections allowed under load
    echo=(settings.APP_ENV == "development"),  # log SQL in dev
)

# Session factory — call AsyncSessionLocal() to get a session
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # lets us read attributes after commit
)


async def get_db():
    """
    FastAPI dependency that provides a DB session.
    The session is automatically closed when the request finishes,
    even if an exception is raised.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """
    Create all tables on startup (development only).
    In production, use Alembic migrations instead.
    """
    from app.core.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
