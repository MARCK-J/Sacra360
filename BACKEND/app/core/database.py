"""Minimal database shim for tests
Provides a SQLAlchemy Base and a get_db dependency to be overridden in tests.
"""
from sqlalchemy.orm import declarative_base
from typing import Generator

Base = declarative_base()


def get_db() -> Generator:
    """Placeholder dependency. Tests override this function via dependency_overrides."""
    try:
        yield None
    finally:
        return
