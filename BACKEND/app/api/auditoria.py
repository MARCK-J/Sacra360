"""
Endpoints para auditoría y seguimiento de cambios en el Sistema Sacra360
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, date

from ..schemas.sacra360_schemas import (
    AuditoriaResponse, MessageResponse
)
from .usuarios import get_current_user

# Configuración del router
router = APIRouter(prefix="/auditoria", tags=["Auditoría"])

# Simulación de base de datos en memoria
fake_auditoria_db = {}
auditoria_id_counter = 1


def crear_log_auditoria(
    id_usuario: int,
    accion: str,
    tabla_afectada: str,
    id_registro_afectado: Optional[int] = None,
    valores_anteriores: Optional[dict] = None,
    valores_nuevos: Optional[dict] = None,
    detalles_adicionales: Optional[str] = None
):
    """
    Función helper para crear registros de auditoría.
    Esta función se llamaría desde otros endpoints cuando se realicen cambios.
    """
    global auditoria_id_counter
    
    nuevo_log = {
        "id_auditoria": auditoria_id_counter,
        "id_usuario": id_usuario,
        "accion": accion,
        "tabla_afectada": tabla_afectada,
        "id_registro_afectado": id_registro_afectado,
        "valores_anteriores": valores_anteriores,
        "valores_nuevos": valores_nuevos,
        "fecha_accion": datetime.now(),
        "ip_address": "192.168.1.100",  # En una implementación real, obtener la IP real
        "user_agent": "Mozilla/5.0...",  # En una implementación real, obtener el user agent real
        "detalles_adicionales": detalles_adicionales
    }
    
    fake_auditoria_db[auditoria_id_counter] = nuevo_log
    auditoria_id_counter += 1
    
    return nuevo_log


@router.get("/", response_model=List[AuditoriaResponse])
async def get_logs_auditoria(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(50, ge=1, le=200, description="Elementos por página"),
    id_usuario: Optional[int] = Query(None, description="Filtrar por usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción"),
    tabla_afectada: Optional[str] = Query(None, description="Filtrar por tabla"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los registros de auditoría del sistema.
    
    Solo administradores y sacerdotes pueden ver los logs completos.
    Otros usuarios solo pueden ver sus propias acciones.
    """
    user_role = current_user.get("rol")
    user_id = current_user.get("id_usuario")
    
    # Filtrar registros según permisos
    filtered_logs = list(fake_auditoria_db.values())
    
    if user_role not in ["admin", "sacerdote"]:
        # Los usuarios normales solo pueden ver sus propias acciones
        filtered_logs = [
            log for log in filtered_logs 
            if log["id_usuario"] == user_id
        ]
    
    # Aplicar filtros
    if id_usuario and user_role in ["admin", "sacerdote"]:
        filtered_logs = [
            log for log in filtered_logs 
            if log["id_usuario"] == id_usuario
        ]
    
    if accion:
        filtered_logs = [
            log for log in filtered_logs 
            if log["accion"].lower() == accion.lower()
        ]
    
    if tabla_afectada:
        filtered_logs = [
            log for log in filtered_logs 
            if log["tabla_afectada"].lower() == tabla_afectada.lower()
        ]
    
    if fecha_desde:
        filtered_logs = [
            log for log in filtered_logs 
            if log["fecha_accion"].date() >= fecha_desde
        ]
        
    if fecha_hasta:
        filtered_logs = [
            log for log in filtered_logs 
            if log["fecha_accion"].date() <= fecha_hasta
        ]
    
    # Ordenar por fecha descendente (más recientes primero)
    filtered_logs.sort(key=lambda x: x["fecha_accion"], reverse=True)
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_logs = filtered_logs[start:end]
    
    return [AuditoriaResponse(**log) for log in paginated_logs]


@router.get("/usuario/{usuario_id}", response_model=List[AuditoriaResponse])
async def get_logs_por_usuario(
    usuario_id: int,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(50, ge=1, le=200, description="Elementos por página"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los registros de auditoría de un usuario específico.
    
    Solo administradores y sacerdotes pueden ver logs de otros usuarios.
    Los usuarios pueden ver solo sus propios logs.
    """
    user_role = current_user.get("rol")
    current_user_id = current_user.get("id_usuario")
    
    # Verificar permisos
    if user_role not in ["admin", "sacerdote"] and current_user_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los logs de este usuario"
        )
    
    # Filtrar logs por usuario
    user_logs = [
        log for log in fake_auditoria_db.values() 
        if log["id_usuario"] == usuario_id
    ]
    
    # Ordenar por fecha descendente
    user_logs.sort(key=lambda x: x["fecha_accion"], reverse=True)
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_logs = user_logs[start:end]
    
    return [AuditoriaResponse(**log) for log in paginated_logs]


@router.get("/tabla/{tabla}", response_model=List[AuditoriaResponse])
async def get_logs_por_tabla(
    tabla: str,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(50, ge=1, le=200, description="Elementos por página"),
    id_registro: Optional[int] = Query(None, description="ID específico del registro"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los registros de auditoría de una tabla específica.
    
    Solo administradores y sacerdotes pueden acceder a este endpoint.
    """
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver logs de auditoría por tabla"
        )
    
    # Filtrar logs por tabla
    table_logs = [
        log for log in fake_auditoria_db.values() 
        if log["tabla_afectada"].lower() == tabla.lower()
    ]
    
    # Filtrar por ID de registro específico si se proporciona
    if id_registro:
        table_logs = [
            log for log in table_logs 
            if log["id_registro_afectado"] == id_registro
        ]
    
    # Ordenar por fecha descendente
    table_logs.sort(key=lambda x: x["fecha_accion"], reverse=True)
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_logs = table_logs[start:end]
    
    return [AuditoriaResponse(**log) for log in paginated_logs]


@router.get("/registro/{tabla}/{registro_id}", response_model=List[AuditoriaResponse])
async def get_historial_registro(
    tabla: str,
    registro_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene el historial completo de cambios de un registro específico.
    
    Solo administradores y sacerdotes pueden acceder a este endpoint.
    """
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver el historial de registros"
        )
    
    # Filtrar logs por tabla y registro específico
    record_history = [
        log for log in fake_auditoria_db.values() 
        if (log["tabla_afectada"].lower() == tabla.lower() and 
            log["id_registro_afectado"] == registro_id)
    ]
    
    # Ordenar por fecha descendente
    record_history.sort(key=lambda x: x["fecha_accion"], reverse=True)
    
    return [AuditoriaResponse(**log) for log in record_history]


@router.get("/estadisticas")
async def get_estadisticas_auditoria(
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas generales de auditoría.
    
    Solo administradores y sacerdotes pueden acceder a este endpoint.
    """
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de auditoría"
        )
    
    # Filtrar logs por fechas si se proporcionan
    filtered_logs = list(fake_auditoria_db.values())
    
    if fecha_desde:
        filtered_logs = [
            log for log in filtered_logs 
            if log["fecha_accion"].date() >= fecha_desde
        ]
        
    if fecha_hasta:
        filtered_logs = [
            log for log in filtered_logs 
            if log["fecha_accion"].date() <= fecha_hasta
        ]
    
    # Calcular estadísticas
    total_acciones = len(filtered_logs)
    
    # Acciones por tipo
    acciones_por_tipo = {}
    for log in filtered_logs:
        accion = log["accion"]
        acciones_por_tipo[accion] = acciones_por_tipo.get(accion, 0) + 1
    
    # Acciones por tabla
    acciones_por_tabla = {}
    for log in filtered_logs:
        tabla = log["tabla_afectada"]
        acciones_por_tabla[tabla] = acciones_por_tabla.get(tabla, 0) + 1
    
    # Usuarios más activos
    usuarios_activos = {}
    for log in filtered_logs:
        usuario = log["id_usuario"]
        usuarios_activos[usuario] = usuarios_activos.get(usuario, 0) + 1
    
    # Ordenar usuarios por actividad
    usuarios_activos_sorted = sorted(
        usuarios_activos.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]  # Top 10
    
    return {
        "periodo": {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        },
        "total_acciones": total_acciones,
        "acciones_por_tipo": acciones_por_tipo,
        "acciones_por_tabla": acciones_por_tabla,
        "usuarios_mas_activos": usuarios_activos_sorted,
        "promedio_acciones_por_dia": total_acciones / max(
            (fecha_hasta - fecha_desde).days if fecha_desde and fecha_hasta else 1, 1
        ) if fecha_desde and fecha_hasta else 0
    }


# Función de ejemplo para crear logs de auditoría
@router.post("/test-log", response_model=AuditoriaResponse)
async def crear_log_test(
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint de prueba para crear un log de auditoría.
    Solo para desarrollo y testing.
    """
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear logs de prueba"
        )
    
    nuevo_log = crear_log_auditoria(
        id_usuario=current_user.get("id_usuario"),
        accion="TEST",
        tabla_afectada="test_table",
        id_registro_afectado=1,
        valores_anteriores={"campo": "valor_anterior"},
        valores_nuevos={"campo": "valor_nuevo"},
        detalles_adicionales="Log de prueba creado desde endpoint de testing"
    )
    
    return AuditoriaResponse(**nuevo_log)