"""
Router de Auditor├¡a de Accesos
Gesti├│n de logs de autenticaci├│n (login, logout, intentos fallidos)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

from app.database import get_db
from app.entities.user_entity import Usuario, Auditoria
from app.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditor├¡a"])


# ===================== DTOs =====================

class AuditoriaResponse(BaseModel):
    """Respuesta de log de auditor├¡a"""
    id_auditoria: int
    usuario_id: int
    nombre_usuario: Optional[str]
    email_usuario: Optional[str]
    accion: str
    registro_afectado: str
    id_registro: int
    fecha: datetime

    class Config:
        from_attributes = True


# ===================== FUNCIONES AUXILIARES =====================

def verificar_es_admin(usuario_actual: dict):
    """Verificar que el usuario actual es administrador"""
    if usuario_actual.get('rol_id') != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a los logs de auditor├¡a"
        )


# ===================== ENDPOINTS =====================

@router.get("", response_model=List[AuditoriaResponse])
async def listar_auditoria(
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción (LOGIN_EXITOSO, LOGIN_FALLIDO, LOGOUT, etc.)"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio (formato: YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin (formato: YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Búsqueda en email o detalles"),
    skip: int = Query(0, ge=0, description="Registros a saltar para paginación"),
    limit: int = Query(50, ge=1, le=500, description="Límite de registros a retornar"),
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_current_user())
):
    """
    Listar logs de auditoría de accesos con filtros
    Solo accesible para administradores
    """
    # Verificar que sea admin
    verificar_es_admin(usuario_actual)
    
    # Query base
    query = db.query(Auditoria).join(
        Usuario, Auditoria.usuario_id == Usuario.id_usuario, isouter=True
    )
    
    # Aplicar filtros
    filtros = []
    
    if usuario_id is not None:
        filtros.append(Auditoria.usuario_id == usuario_id)
    
    if accion:
        filtros.append(Auditoria.accion.ilike(f"%{accion}%"))
    
    if fecha_inicio:
        filtros.append(Auditoria.fecha >= fecha_inicio)
    
    if fecha_fin:
        filtros.append(Auditoria.fecha <= fecha_fin)
    
    if search:
        filtros.append(
            or_(
                Usuario.email.ilike(f"%{search}%"),
                Usuario.nombre.ilike(f"%{search}%"),
                Auditoria.registro_afectado.ilike(f"%{search}%")
            )
        )
    
    # Aplicar todos los filtros
    if filtros:
        query = query.filter(and_(*filtros))
    
    # Ordenar por fecha descendente (m├ís recientes primero)
    query = query.order_by(desc(Auditoria.fecha))
    
    # Paginaci├│n
    logs = query.offset(skip).limit(limit).all()
    
    # Construir respuesta con informaci├│n del usuario
    resultado = []
    for log in logs:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == log.usuario_id).first() if log.usuario_id else None
        
        resultado.append(AuditoriaResponse(
            id_auditoria=log.id_auditoria,
            usuario_id=log.usuario_id,
            nombre_usuario=f"{usuario.nombre} {usuario.apellido_paterno}" if usuario else None,
            email_usuario=usuario.email if usuario else None,
            accion=log.accion,
            registro_afectado=log.registro_afectado,
            id_registro=log.id_registro,
            fecha=log.fecha
        ))
    
    return resultado


@router.get("/{log_id}", response_model=AuditoriaResponse)
async def obtener_auditoria(
    log_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_current_user())
):
    """
    Obtener un log de auditor├¡a espec├¡fico por ID
    Solo accesible para administradores
    """
    # Verificar que sea admin
    verificar_es_admin(usuario_actual)
    
    # Buscar el log
    log = db.query(Auditoria).filter(Auditoria.id_auditoria == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log de auditor├¡a con ID {log_id} no encontrado"
        )
    
    # Obtener informaci├│n del usuario
    usuario = db.query(Usuario).filter(Usuario.id_usuario == log.usuario_id).first() if log.usuario_id else None
    
    return AuditoriaResponse(
        id_auditoria=log.id_auditoria,
        usuario_id=log.usuario_id,
        nombre_usuario=f"{usuario.nombre} {usuario.apellido_paterno}" if usuario else None,
        email_usuario=usuario.email if usuario else None,
        accion=log.accion,
        registro_afectado=log.registro_afectado,
        id_registro=log.id_registro,
        fecha=log.fecha
    )


@router.get("/usuario/{usuario_id}", response_model=List[AuditoriaResponse])
async def obtener_auditoria_por_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Obtener logs de auditoria de un usuario especifico
    Solo accesible para administradores
    """
    # Verificar que sea admin
    verificar_es_admin(usuario_actual)
    
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Obtener logs del usuario
    logs = db.query(Auditoria).filter(
        Auditoria.usuario_id == usuario_id
    ).order_by(desc(Auditoria.fecha)).offset(skip).limit(limit).all()
    
    # Construir respuesta
    resultado = []
    for log in logs:
        resultado.append(AuditoriaResponse(
            id_auditoria=log.id_auditoria,
            usuario_id=log.usuario_id,
            nombre_usuario=f"{usuario.nombre} {usuario.apellido_paterno}",
            email_usuario=usuario.email,
            accion=log.accion,
            registro_afectado=log.registro_afectado,
            id_registro=log.id_registro,
            fecha=log.fecha
        ))
    
    return resultado


@router.get("/stats/resumen")
async def obtener_estadisticas(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Obtener estad├¡sticas de auditor├¡a (resumen)
    Solo accesible para administradores
    """
    # Verificar que sea admin
    verificar_es_admin(usuario_actual)
    
    # Query base
    query = db.query(Auditoria)
    
    # Aplicar filtros de fecha
    if fecha_inicio:
        query = query.filter(Auditoria.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Auditoria.fecha <= fecha_fin)
    
    # Contar totales basados en el campo accion
    total_logs = query.count()
    logins_exitosos = query.filter(Auditoria.accion.ilike("%LOGIN%EXITOSO%")).count()
    logins_fallidos = query.filter(Auditoria.accion.ilike("%LOGIN%FALLIDO%")).count()
    logouts = query.filter(Auditoria.accion.ilike("%LOGOUT%")).count()
    
    return {
        "total_eventos": total_logs,
        "logins_exitosos": logins_exitosos,
        "logins_fallidos": logins_fallidos,
        "logouts": logouts,
        "tasa_exito": round((logins_exitosos / (logins_exitosos + logins_fallidos) * 100), 2) if (logins_exitosos + logins_fallidos) > 0 else 0,
        "periodo": {
            "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
            "fecha_fin": fecha_fin.isoformat() if fecha_fin else None
        }
    }