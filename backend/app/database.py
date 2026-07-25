"""SQLAlchemy engine/session setup for the PayVerify AI backend.

Defaults to a local SQLite file for non-Docker development. Set the
DATABASE_URL environment variable (e.g.
``postgresql+psycopg://user:pass@host:5432/dbname``) to use PostgreSQL, as
configured automatically in docker-compose.yml for containerized runs.
"""
from __future__ import annotations

import os
import pathlib
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "payverify.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DB_PATH}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE_URL)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so they are registered on Base.metadata before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
