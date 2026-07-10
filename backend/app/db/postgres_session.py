from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Separate engine pointing at PostgreSQL
pg_engine = create_engine(
    settings.POSTGRES_URL,
    pool_pre_ping=True,      # automatically reconnect after idle timeouts
    pool_size=10,            # keep 10 connections alive in the pool
    max_overflow=20,         # allow 20 extra connections under burst load
    echo=settings.DEBUG,     # log SQL in dev, silent in prod
)

PGSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)

# Auth models inherit from this Base — completely separate from the chat Base
AuthBase = declarative_base()


def get_pg_db():
    """
    FastAPI dependency — yields a PostgreSQL session, always closes it.
    Usage:
        @router.get("/me")
        def me(db: Session = Depends(get_pg_db)):
            ...
    """
    db = PGSessionLocal()
    try:
        yield db
    finally:
        db.close()