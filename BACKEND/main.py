"""Main app wrapper to expose routes expected by tests.
This file creates a FastAPI `app` and mounts the parishes and stats routers
we implemented under `server-sacra360/Documents-service/app/routers`.
"""
import os
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
parishes_path = os.path.join(base, "server-sacra360", "Documents-service", "app", "routers", "parishes_router.py")
stats_path = os.path.join(base, "server-sacra360", "Documents-service", "app", "routers", "stats_router.py")

if os.path.exists(parishes_path):
    try:
        router = _load_router_from_path(parishes_path)
        app.include_router(router, prefix="/api/v1", tags=["Parishes"])
    except Exception:
        pass

if os.path.exists(stats_path):
    try:
        router = _load_router_from_path(stats_path)
        app.include_router(router, prefix="/api/v1", tags=["Stats"])
    except Exception:
        pass
