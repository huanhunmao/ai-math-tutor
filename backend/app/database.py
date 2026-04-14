import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://") and "+psycopg" not in raw_url:
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


def get_database_url():
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return normalize_database_url(configured_url)

    sqlite_path = "./math_tutor.db"
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        sqlite_path = "/tmp/math_tutor.db"

    return f"sqlite:///{sqlite_path}"


DATABASE_URL = get_database_url()

ENGINE_KWARGS = {}
if DATABASE_URL.startswith("sqlite"):
    ENGINE_KWARGS["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **ENGINE_KWARGS,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
