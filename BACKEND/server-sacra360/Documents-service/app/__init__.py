"""Documents-service app package

This file makes the Documents-service `app` folder a proper Python package so
imports like `from app.dto import documents_dto` work when the Documents-service
directory is available on sys.path.
"""

__all__ = ["dto", "entities", "routers"]
