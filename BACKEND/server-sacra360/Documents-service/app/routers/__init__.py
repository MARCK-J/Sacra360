"""Routers package for Documents-service"""

from . import parishes_router
from . import stats_router
from . import sacraments_router

__all__ = ["parishes_router", "stats_router", "sacraments_router"]
