"""Main app wrapper to expose routes expected by tests.
This file creates a FastAPI `app` and mounts the parishes and stats routers
we implemented under `server-sacra360/Documents-service/app/routers`.
"""
import os
import sys
import importlib.util
from fastapi import FastAPI


def _load_router_from_path(path: str):
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "router")


app = FastAPI(title="Sacra360 API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Sacra360 API", "version": "1.0.0", "status": "active"}


@app.get("/health")
def health():
    return {"status": "healthy", "services": ["documents-service", "auth-service"]}


# Attempt to include routers implemented in Documents-service
base = os.path.dirname(__file__)
docs_parent = os.path.join(base, "server-sacra360", "Documents-service")
docs_app_path = os.path.join(docs_parent, "app")
parishes_path = os.path.join(docs_app_path, "routers", "parishes_router.py")
stats_path = os.path.join(docs_app_path, "routers", "stats_router.py")

# Ensure project base and Documents-service parent are on sys.path so that
# absolute imports used inside Documents-service routers (like
# `from app.core.database import get_db`) resolve to the project's `app`.
# This is a localized convenience for test/runtime import resolution.
if base not in sys.path:
    sys.path.insert(0, base)
if docs_parent not in sys.path:
    sys.path.insert(0, docs_parent)

if os.path.exists(parishes_path):
    try:
        # Temporarily ensure the project base and the Documents-service parent
        # are on sys.path so absolute imports inside the router file resolve
        # correctly during dynamic import. Remove them afterwards to avoid
        # persistent side-effects.
        inserted = []
        if base not in sys.path:
            sys.path.insert(0, base)
            inserted.append(base)
        if docs_parent not in sys.path:
            sys.path.insert(0, docs_parent)
            inserted.append(docs_parent)
        try:
            router = _load_router_from_path(parishes_path)
            app.include_router(router, prefix="/api/v1", tags=["Parishes"])
        finally:
            for p in inserted:
                try:
                    sys.path.remove(p)
                except ValueError:
                    pass
    except Exception:
        pass

if os.path.exists(stats_path):
    try:
        inserted = []
        if base not in sys.path:
            sys.path.insert(0, base)
            inserted.append(base)
        if docs_parent not in sys.path:
            sys.path.insert(0, docs_parent)
            inserted.append(docs_parent)
        try:
            router = _load_router_from_path(stats_path)
            app.include_router(router, prefix="/api/v1", tags=["Stats"])
        finally:
            for p in inserted:
                try:
                    sys.path.remove(p)
                except ValueError:
                    pass
    except Exception:
        pass
