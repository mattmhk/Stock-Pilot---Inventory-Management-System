import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Read settings from backend/.env (if it exists) into environment variables
load_dotenv()


def normalize_database_url(url: str) -> str:
    """Make SQLAlchemy use the psycopg 3 driver for PostgreSQL URLs.

    Providers such as Neon hand out "postgresql://" (or "postgres://") URLs,
    which SQLAlchemy would otherwise map to the psycopg2 driver.
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite:///./stockpilot.db")
)

# Migrations should use a direct connection rather than a connection pooler
# (Neon provides DATABASE_URL_UNPOOLED); fall back to DATABASE_URL otherwise.
MIGRATION_DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL_UNPOOLED") or DATABASE_URL
)


engine_options = {}

# check_same_thread is a SQLite-only option; PostgreSQL doesn't accept it
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    **engine_options
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
