"""
Middleware de verificación de permisos RBAC
Valida que el usuario tenga los permisos necesarios para acceder a los endpoints
"""

from functools import wraps
from fastapi import HTTPException, status
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Matriz de permisos por rol
# Estructura: {rol_id: {modulo: [permisos]}}
PERMISSIONS_MATRIX = {
    1: {  # Administrador - Acceso total
        "usuarios": ["create", "read", "update", "delete"],
        "auditoria": ["create", "read", "update", "delete"],
        "digitalizacion": ["create", "read", "update", "delete"],
        "revision_ocr": ["create", "read", "update", "delete"],
        "registros": ["create", "read", "update", "delete"],
        "personas": ["create", "read", "update", "delete"],
        "libros": ["create", "read", "update", "delete"],
        "certificados": ["create", "read", "update", "delete"],
        "reportes": ["create", "read", "update", "delete"],
    },
    2: {  # Digitalizador
        "digitalizacion": ["create", "read", "update", "delete"],
        "revision_ocr": ["read"],
        "registros": ["read"],
        "personas": ["read"],
        "libros": ["read"],
        "certificados": ["read"],
        "reportes": ["read"],
    },
    3: {  # Revisor
        "digitalizacion": ["read"],
        "revision_ocr": ["create", "read", "update"],
        "registros": ["create", "read", "update"],
        "personas": ["create", "read", "update"],
        "libros": ["read"],
        "certificados": ["create", "read"],
        "reportes": ["read"],
    },
    4: {  # Consultor - Solo lectura
        "digitalizacion": ["read"],
        "revision_ocr": ["read"],
        "registros": ["read"],
        "personas": ["read"],
        "libros": ["read"],
        "certificados": ["read"],
        "reportes": ["read"],
    }
}


def has_permission(rol_id: int, modulo: str, accion: str) -> bool:
    """
    Verifica si un rol tiene permiso para realizar una acción en un módulo
    
    Args:
        rol_id: ID del rol del usuario
        modulo: Nombre del módulo (usuarios, digitalizacion, etc.)
        accion: Acción a verificar (create, read, update, delete)
    
    Returns:
        True si tiene permiso, False en caso contrario
    """
    try:
        # Obtener permisos del rol
        rol_permisos = PERMISSIONS_MATRIX.get(rol_id, {})
        modulo_permisos = rol_permisos.get(modulo, [])
        
        # Verificar si la acción está permitida
        has_perm = accion in modulo_permisos
        
        logger.debug(f"Verificando permiso: rol={rol_id}, modulo={modulo}, accion={accion}, resultado={has_perm}")
        
        return has_perm
    except Exception as e:
        logger.error(f"Error verificando permisos: {e}")
        return False


def require_permission(modulo: str, accion: str):
    """
    Decorador para proteger endpoints con permisos específicos
    
    Uso:
        @router.post("/usuarios")
        @require_permission("usuarios", "create")
        async def crear_usuario(...):
            ...
    
    Args:
        modulo: Módulo a verificar
        accion: Acción requerida (create, read, update, delete)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener el usuario actual de los kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar permisos
            if not has_permission(current_user.rol_id, modulo, accion):
                logger.warning(
                    f"Acceso denegado: usuario={current_user.email}, "
                    f"rol={current_user.rol_id}, modulo={modulo}, accion={accion}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tienes permisos para {accion} en {modulo}"
                )
            
            # Ejecutar función
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_user_permissions(rol_id: int) -> dict:
    """
    Obtiene todos los permisos de un rol
    
    Args:
        rol_id: ID del rol
    
    Returns:
        Diccionario con los permisos del rol
    """
    return PERMISSIONS_MATRIX.get(rol_id, {})


def can_access_module(rol_id: int, modulo: str) -> bool:
    """
    Verifica si un rol puede acceder a un módulo (al menos lectura)
    
    Args:
        rol_id: ID del rol
        modulo: Nombre del módulo
    
    Returns:
        True si puede acceder, False en caso contrario
    """
    return has_permission(rol_id, modulo, "read")
