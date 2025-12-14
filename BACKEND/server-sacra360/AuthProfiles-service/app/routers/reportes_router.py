"""
Router de Reportes y Estadísticas
Sistema completo de generación de reportes para análisis y toma de decisiones
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from typing import Optional, List
from datetime import datetime, timedelta, date
from pydantic import BaseModel

from app.database import get_db
from app.entities.user_entity import Usuario, Rol, Auditoria
from app.utils.auth_utils import get_current_user
from app.middleware import require_permission

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


# ===================== DTOs =====================

class ReporteUsuariosResponse(BaseModel):
    """Reporte de usuarios del sistema"""
    total_usuarios: int
    usuarios_activos: int
    usuarios_inactivos: int
    porcentaje_activos: float
    usuarios_por_rol: List[dict]
    fecha_generacion: datetime

    class Config:
        from_attributes = True


class ReporteAccesosResponse(BaseModel):
    """Reporte de accesos al sistema"""
    total_accesos: int
    logins_exitosos: int
    logins_fallidos: int
    tasa_exito: float
    accesos_por_dia: List[dict]
    usuarios_mas_activos: List[dict]
    horas_pico: List[dict]
    fecha_generacion: datetime

    class Config:
        from_attributes = True


class ReporteActividadResponse(BaseModel):
    """Reporte de actividad por usuario"""
    usuario_id: int
    nombre_completo: str
    email: str
    rol: str
    total_acciones: int
    ultimo_acceso: Optional[datetime]
    acciones_por_modulo: List[dict]
    fecha_generacion: datetime

    class Config:
        from_attributes = True


class EstadisticasGeneralesResponse(BaseModel):
    """Estadísticas generales del sistema"""
    total_usuarios: int
    total_accesos: int
    total_acciones: int
    promedio_accesos_por_dia: float
    promedio_accesos_por_usuario: float
    total_eventos_auditoria: int
    fecha_generacion: datetime

    class Config:
        from_attributes = True


# ===================== ENDPOINTS =====================

@router.get("/usuarios", response_model=ReporteUsuariosResponse)
@require_permission("reportes", "read")
async def reporte_usuarios(
    current_user: dict = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """
    Genera reporte completo de usuarios del sistema
    
    **Requiere:** Permisos de lectura en reportes
    
    **Retorna:**
    - Total de usuarios
    - Usuarios activos/inactivos
    - Distribución por roles
    """
    # Total de usuarios
    total = db.query(Usuario).count()
    activos = db.query(Usuario).filter(Usuario.activo == True).count()
    inactivos = total - activos
    
    # Porcentaje de activos
    porcentaje_activos = (activos / total * 100) if total > 0 else 0
    
    # Usuarios por rol
    usuarios_por_rol = db.query(
        Rol.nombre,
        func.count(Usuario.id_usuario).label('cantidad')
    ).join(Usuario).group_by(Rol.nombre).all()
    
    usuarios_por_rol_dict = [
        {"rol": r.nombre, "cantidad": r.cantidad, "porcentaje": round(r.cantidad / total * 100, 2)}
        for r in usuarios_por_rol
    ]
    
    return ReporteUsuariosResponse(
        total_usuarios=total,
        usuarios_activos=activos,
        usuarios_inactivos=inactivos,
        porcentaje_activos=round(porcentaje_activos, 2),
        usuarios_por_rol=usuarios_por_rol_dict,
        fecha_generacion=datetime.now()
    )


@router.get("/accesos", response_model=ReporteAccesosResponse)
@require_permission("reportes", "read")
async def reporte_accesos(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio del reporte"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin del reporte"),
    current_user: dict = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """
    Genera reporte de accesos al sistema
    
    **Requiere:** Permisos de lectura en reportes
    
    **Parámetros:**
    - fecha_inicio: Fecha de inicio (default: hace 30 días)
    - fecha_fin: Fecha de fin (default: hoy)
    
    **Retorna:**
    - Total de accesos
    - Logins exitosos/fallidos
    - Accesos por día
    - Usuarios más activos
    - Horas pico
    """
    # Fechas por defecto
    if not fecha_fin:
        fecha_fin = date.today()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Convertir a datetime
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
    
    # Total de accesos (logins)
    query_base = db.query(Auditoria).filter(
        and_(
            Auditoria.fecha >= fecha_inicio_dt,
            Auditoria.fecha <= fecha_fin_dt,
            Auditoria.accion.in_(['LOGIN_EXITOSO', 'LOGIN_FALLIDO'])
        )
    )
    
    total_accesos = query_base.count()
    logins_exitosos = query_base.filter(Auditoria.accion == 'LOGIN_EXITOSO').count()
    logins_fallidos = query_base.filter(Auditoria.accion == 'LOGIN_FALLIDO').count()
    
    tasa_exito = (logins_exitosos / total_accesos * 100) if total_accesos > 0 else 0
    
    # Accesos por día
    accesos_por_dia = db.query(
        func.date(Auditoria.fecha).label('fecha'),
        func.count(Auditoria.id_auditoria).label('cantidad')
    ).filter(
        and_(
            Auditoria.fecha >= fecha_inicio_dt,
            Auditoria.fecha <= fecha_fin_dt,
            Auditoria.accion == 'LOGIN_EXITOSO'
        )
    ).group_by(func.date(Auditoria.fecha)).order_by('fecha').all()
    
    accesos_por_dia_dict = [
        {"fecha": str(a.fecha), "cantidad": a.cantidad}
        for a in accesos_por_dia
    ]
    
    # Usuarios más activos
    usuarios_activos = db.query(
        Usuario.nombre,
        Usuario.apellido_paterno,
        Usuario.email,
        func.count(Auditoria.id_auditoria).label('accesos')
    ).join(Auditoria).filter(
        and_(
            Auditoria.fecha >= fecha_inicio_dt,
            Auditoria.fecha <= fecha_fin_dt,
            Auditoria.accion == 'LOGIN_EXITOSO'
        )
    ).group_by(
        Usuario.id_usuario, Usuario.nombre, Usuario.apellido_paterno, Usuario.email
    ).order_by(desc('accesos')).limit(10).all()
    
    usuarios_activos_dict = [
        {
            "nombre": f"{u.nombre} {u.apellido_paterno}",
            "email": u.email,
            "accesos": u.accesos
        }
        for u in usuarios_activos
    ]
    
    # Horas pico
    horas_pico = db.query(
        extract('hour', Auditoria.fecha).label('hora'),
        func.count(Auditoria.id_auditoria).label('cantidad')
    ).filter(
        and_(
            Auditoria.fecha >= fecha_inicio_dt,
            Auditoria.fecha <= fecha_fin_dt,
            Auditoria.accion == 'LOGIN_EXITOSO'
        )
    ).group_by('hora').order_by(desc('cantidad')).limit(5).all()
    
    horas_pico_dict = [
        {"hora": f"{int(h.hora):02d}:00", "cantidad": h.cantidad}
        for h in horas_pico
    ]
    
    return ReporteAccesosResponse(
        total_accesos=total_accesos,
        logins_exitosos=logins_exitosos,
        logins_fallidos=logins_fallidos,
        tasa_exito=round(tasa_exito, 2),
        accesos_por_dia=accesos_por_dia_dict,
        usuarios_mas_activos=usuarios_activos_dict,
        horas_pico=horas_pico_dict,
        fecha_generacion=datetime.now()
    )


@router.get("/actividad/{usuario_id}", response_model=ReporteActividadResponse)
@require_permission("reportes", "read")
async def reporte_actividad_usuario(
    usuario_id: int,
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """
    Genera reporte de actividad de un usuario específico
    
    **Requiere:** Permisos de lectura en reportes
    
    **Retorna:**
    - Información del usuario
    - Total de acciones
    - Último acceso
    - Acciones por módulo
    """
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Fechas por defecto
    if not fecha_fin:
        fecha_fin = date.today()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
    
    # Total de acciones
    total_acciones = db.query(Auditoria).filter(
        and_(
            Auditoria.usuario_id == usuario_id,
            Auditoria.fecha >= fecha_inicio_dt,
            Auditoria.fecha <= fecha_fin_dt
        )
    ).count()
    
    # Último acceso
    ultimo_acceso = db.query(Auditoria.fecha).filter(
        and_(
            Auditoria.usuario_id == usuario_id,
            Auditoria.accion == 'LOGIN_EXITOSO'
        )
    ).order_by(desc(Auditoria.fecha)).first()
    
    # Acciones por tipo
    acciones_por_tipo = db.query(
        Auditoria.accion,
        func.count(Auditoria.id_auditoria).label('cantidad')
    ).filter(
        and_(
            Auditoria.usuario_id == usuario_id,
            Auditoria.fecha >= fecha_inicio_dt,
            Auditoria.fecha <= fecha_fin_dt
        )
    ).group_by(Auditoria.accion).order_by(desc('cantidad')).all()
    
    acciones_por_modulo_dict = [
        {"modulo": a.accion or "Sin especificar", "cantidad": a.cantidad}
        for a in acciones_por_tipo
    ]
    
    return ReporteActividadResponse(
        usuario_id=usuario.id_usuario,
        nombre_completo=f"{usuario.nombre} {usuario.apellido_paterno}",
        email=usuario.email,
        rol=usuario.rol.nombre if usuario.rol else "Sin rol",
        total_acciones=total_acciones,
        ultimo_acceso=ultimo_acceso[0] if ultimo_acceso else None,
        acciones_por_modulo=acciones_por_modulo_dict,
        fecha_generacion=datetime.now()
    )


@router.get("/estadisticas", response_model=EstadisticasGeneralesResponse)
@require_permission("reportes", "read")
async def estadisticas_generales(
    dias: int = Query(30, description="Número de días hacia atrás"),
    current_user: dict = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """
    Genera estadísticas generales del sistema
    
    **Requiere:** Permisos de lectura en reportes
    
    **Parámetros:**
    - dias: Número de días hacia atrás (default: 30)
    
    **Retorna:**
    - Totales generales
    - Promedios
    - Módulos más usados
    """
    fecha_inicio = datetime.now() - timedelta(days=dias)
    fecha_fin = datetime.now()
    
    # Totales
    total_usuarios = db.query(Usuario).count()
    total_accesos = db.query(Auditoria).filter(
        and_(
            Auditoria.fecha >= fecha_inicio,
            Auditoria.accion.like('%login%')
        )
    ).count()
    total_acciones = db.query(Auditoria).filter(
        Auditoria.fecha >= fecha_inicio
    ).count()
    
    # Promedio de accesos diarios
    promedio_accesos = total_accesos / dias if dias > 0 else 0
    
    # Acciones más comunes
    acciones_comunes = db.query(
        Auditoria.accion,
        func.count(Auditoria.id_auditoria).label('cantidad')
    ).filter(
        Auditoria.fecha >= fecha_inicio
    ).group_by(Auditoria.accion).order_by(desc('cantidad')).limit(10).all()
    
    acciones_dict = [
        {"accion": a.accion or "Sin especificar", "cantidad": a.cantidad}
        for a in acciones_comunes
    ]
    
    return EstadisticasGeneralesResponse(
        total_usuarios=total_usuarios,
        total_accesos=total_accesos,
        total_acciones=total_acciones,
        promedio_accesos_por_dia=round(promedio_accesos, 2),
        promedio_accesos_por_usuario=round(total_accesos / total_usuarios, 2) if total_usuarios > 0 else 0,
        total_eventos_auditoria=total_acciones,
        fecha_generacion=datetime.now()
    )


@router.get("/permisos/{usuario_id}")
@require_permission("reportes", "read")
async def obtener_permisos_usuario(
    usuario_id: int,
    current_user: dict = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """
    Obtiene los permisos de un usuario específico
    
    **Requiere:** Permisos de lectura en reportes
    
    **Retorna:**
    - Información del usuario
    - Rol asignado
    - Permisos detallados por módulo
    """
    from app.middleware import get_user_permissions
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Obtener permisos del rol
    permisos = get_user_permissions(usuario.rol_id)
    
    return {
        "usuario_id": usuario.id_usuario,
        "nombre": f"{usuario.nombre} {usuario.apellido_paterno}",
        "email": usuario.email,
        "rol_id": usuario.rol_id,
        "rol_nombre": usuario.rol.nombre if usuario.rol else "Sin rol",
        "permisos": permisos,
        "fecha_consulta": datetime.now()
    }
