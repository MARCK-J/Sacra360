"""
API routers module para Sistema Sacra360

Este módulo contiene todos los routers de la API del sistema de gestión 
sacramental Sacra360, incluyendo:

- usuarios: Gestión de usuarios con roles parroquiales
- personas: Administración de personas y sus datos
- sacramentos: Gestión completa de sacramentos
- documentos: Digitalización y procesamiento OCR
- auditoria: Sistema de trazabilidad y logs
"""

from .users import router as users_router
from .resources import router as resources_router
from .usuarios import router as usuarios_router
from .personas import router as personas_router
from .sacramentos import router as sacramentos_router
from .documentos import router as documentos_router
from .auditoria import router as auditoria_router

__all__ = [
    "users_router", 
    "resources_router",
    "usuarios_router",
    "personas_router", 
    "sacramentos_router",
    "documentos_router",
    "auditoria_router"
]