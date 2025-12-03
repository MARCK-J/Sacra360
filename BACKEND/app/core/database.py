from sqlalchemy.orm import declarative_base

Base = declarative_base()

def get_db():
    """Minimal get_db dependency used by tests. Tests will usually override this."""
    # Simple generator to satisfy dependency injection signature
    db = None
    try:
        yield db
    finally:
        pass
