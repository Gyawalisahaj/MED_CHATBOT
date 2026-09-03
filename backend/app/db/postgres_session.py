from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


def _create_auth_engine():
    try:
        engine = create_engine(
            settings.POSTGRES_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
        )
        with engine.connect():
            return engine
    except Exception as exc:
        fallback_url = settings.DATABASE_URL
        print(f"PostgreSQL unavailable ({exc}). Using SQLite auth database: {fallback_url}")
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )


pg_engine = _create_auth_engine()

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