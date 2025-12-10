"""
Router de Gesti├│n de Usuarios
CRUD completo para administraci├│n de usuarios del sistema
Requiere rol de Administrador
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, date
import logging

from app.entities.user_entity import Usuario, Rol, Auditoria
from app.utils.auth_utils import (
    verify_password,
    get_password_hash,
    get_current_user
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


# Dependency para obtener la sesi├│n de BD
def get_db():
    """Dependency para obtener la sesi├│n de base de datos"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def registrar_auditoria(
    db: Session,
    usuario_id: Optional[int],
    accion: str,
    detalles: Optional[str] = None
):
    """Registrar evento en la tabla auditoria"""
    try:
        from datetime import datetime
        auditoria = Auditoria(
            usuario_id=usuario_id,
            accion=accion,
            registro_afectado="USUARIOS",
            id_registro=usuario_id if usuario_id else 0,
            fecha=datetime.now()
        )
        db.add(auditoria)
        db.commit()
    except Exception as e:
        logger.error(f"Error al registrar auditor├¡a: {e}")
        db.rollback()


def verificar_es_admin(usuario_actual: Usuario):
    """Verificar que el usuario actual sea administrador"""
    if usuario_actual.rol_id != 1:  # 1 = Administrador
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acci├│n. Se requiere rol de Administrador."
        )


# ==================== DTOs ====================

from pydantic import BaseModel, EmailStr, Field

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido_paterno: str = Field(..., min_length=2, max_length=100)
    apellido_materno: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    contrasenia: str = Field(..., min_length=8)
    rol_id: int = Field(..., ge=1, le=4)
    activo: bool = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido_paterno: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido_materno: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    rol_id: Optional[int] = Field(None, ge=1, le=4)
    activo: Optional[bool] = None

class UsuarioUpdatePassword(BaseModel):
    contrasenia: str = Field(..., min_length=8)

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    email: str
    rol_id: int
    nombre_rol: str
    activo: bool
    fecha_creacion: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.get("", response_model=List[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None,
    rol_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Listar todos los usuarios del sistema
    - Requiere: rol de Administrador
    - Soporta filtros por activo, rol y b├║squeda por nombre/email
    """
    verificar_es_admin(usuario_actual)
    
    try:
        # Query base
        query = db.query(Usuario)
        
        # Aplicar filtros
        if activo is not None:
            query = query.filter(Usuario.activo == activo)
        
        if rol_id is not None:
            query = query.filter(Usuario.rol_id == rol_id)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Usuario.nombre.ilike(search_filter),
                    Usuario.apellido_paterno.ilike(search_filter),
                    Usuario.apellido_materno.ilike(search_filter),
                    Usuario.email.ilike(search_filter)
                )
            )
        
        # Ejecutar query con paginaci├│n
        usuarios = query.offset(skip).limit(limit).all()
        
        # Obtener roles
        roles = {rol.id_rol: rol.nombre for rol in db.query(Rol).all()}
        
        # Preparar respuesta
        response = []
        for usuario in usuarios:
            response.append(UsuarioResponse(
                id_usuario=usuario.id_usuario,
                nombre=usuario.nombre,
                apellido_paterno=usuario.apellido_paterno,
                apellido_materno=usuario.apellido_materno,
                email=usuario.email,
                rol_id=usuario.rol_id,
                nombre_rol=roles.get(usuario.rol_id, "Sin rol"),
                activo=usuario.activo,
                fecha_creacion=usuario.fecha_creacion
            ))
        
        logger.info(f"Usuarios listados por admin ID: {usuario_actual.id_usuario}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener lista de usuarios"
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Obtener detalles de un usuario espec├¡fico
    - Requiere: rol de Administrador
    """
    verificar_es_admin(usuario_actual)
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Obtener nombre del rol
    rol = db.query(Rol).filter(Rol.id_rol == usuario.rol_id).first()
    nombre_rol = rol.nombre if rol else "Sin rol"
    
    return UsuarioResponse(
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        email=usuario.email,
        rol_id=usuario.rol_id,
        nombre_rol=nombre_rol,
        activo=usuario.activo,
        fecha_creacion=usuario.fecha_creacion
    )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo usuario
    - Requiere: rol de Administrador
    """
    verificar_es_admin(usuario_actual)
    
    try:
        # Verificar que el email no exista
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == data.email.lower()
        ).first()
        
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email {data.email} ya est├í registrado"
            )
        
        # Verificar que el rol existe
        rol = db.query(Rol).filter(Rol.id_rol == data.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol con ID {data.rol_id} no existe"
            )
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=data.nombre,
            apellido_paterno=data.apellido_paterno,
            apellido_materno=data.apellido_materno,
            email=data.email.lower(),
            contrasenia=get_password_hash(data.contrasenia),
            rol_id=data.rol_id,
            activo=data.activo,
            fecha_creacion=datetime.now()
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        # Registrar auditor├¡a
        registrar_auditoria(
            db=db,
            usuario_id=usuario_actual.id_usuario,
            accion="CREAR_USUARIO",
            detalles=f"Usuario creado: {nuevo_usuario.email} (ID: {nuevo_usuario.id_usuario})"
        )
        
        logger.info(f"Usuario creado: {nuevo_usuario.email} por admin ID: {usuario_actual.id_usuario}")
        
        return UsuarioResponse(
            id_usuario=nuevo_usuario.id_usuario,
            nombre=nuevo_usuario.nombre,
            apellido_paterno=nuevo_usuario.apellido_paterno,
            apellido_materno=nuevo_usuario.apellido_materno,
            email=nuevo_usuario.email,
            rol_id=nuevo_usuario.rol_id,
            nombre_rol=rol.nombre,
            activo=nuevo_usuario.activo,
            fecha_creacion=nuevo_usuario.fecha_creacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear usuario"
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Actualizar informaci├│n de un usuario
    - Requiere: rol de Administrador
    - No incluye cambio de contrase├▒a (usar endpoint espec├¡fico)
    """
    verificar_es_admin(usuario_actual)
    
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Verificar email ├║nico si se est├í actualizando
        if data.email and data.email != usuario.email:
            email_existente = db.query(Usuario).filter(
                Usuario.email == data.email.lower(),
                Usuario.id_usuario != usuario_id
            ).first()
            
            if email_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El email {data.email} ya est├í en uso"
                )
        
        # Verificar rol si se est├í actualizando
        if data.rol_id:
            rol = db.query(Rol).filter(Rol.id_rol == data.rol_id).first()
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol con ID {data.rol_id} no existe"
                )
        
        # Actualizar campos
        if data.nombre is not None:
            usuario.nombre = data.nombre
        if data.apellido_paterno is not None:
            usuario.apellido_paterno = data.apellido_paterno
        if data.apellido_materno is not None:
            usuario.apellido_materno = data.apellido_materno
        if data.email is not None:
            usuario.email = data.email.lower()
        if data.rol_id is not None:
            usuario.rol_id = data.rol_id
        if data.activo is not None:
            usuario.activo = data.activo
        
        db.commit()
        db.refresh(usuario)
        
        # Registrar auditor├¡a
        registrar_auditoria(
            db=db,
            usuario_id=usuario_actual.id_usuario,
            accion="ACTUALIZAR_USUARIO",
            detalles=f"Usuario actualizado: {usuario.email} (ID: {usuario.id_usuario})"
        )
        
        logger.info(f"Usuario {usuario_id} actualizado por admin ID: {usuario_actual.id_usuario}")
        
        # Obtener nombre del rol
        rol = db.query(Rol).filter(Rol.id_rol == usuario.rol_id).first()
        nombre_rol = rol.nombre if rol else "Sin rol"
        
        return UsuarioResponse(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            apellido_paterno=usuario.apellido_paterno,
            apellido_materno=usuario.apellido_materno,
            email=usuario.email,
            rol_id=usuario.rol_id,
            nombre_rol=nombre_rol,
            activo=usuario.activo,
            fecha_creacion=usuario.fecha_creacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar usuario"
        )


@router.patch("/{usuario_id}/password")
async def cambiar_contrasenia(
    usuario_id: int,
    data: UsuarioUpdatePassword,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Cambiar contrase├▒a de un usuario
    - Requiere: rol de Administrador
    """
    verificar_es_admin(usuario_actual)
    
    try:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Actualizar contrase├▒a
        usuario.contrasenia = get_password_hash(data.contrasenia)
        db.commit()
        
        # Registrar auditor├¡a
        registrar_auditoria(
            db=db,
            usuario_id=usuario_actual.id_usuario,
            accion="CAMBIAR_CONTRASENIA",
            detalles=f"Contrase├▒a cambiada para usuario: {usuario.email} (ID: {usuario.id_usuario})"
        )
        
        logger.info(f"Contrase├▒a cambiada para usuario {usuario_id} por admin ID: {usuario_actual.id_usuario}")
        
        return {"message": "Contrase├▒a actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al cambiar contrase├▒a: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar contrase├▒a"
        )


@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Eliminar (desactivar) un usuario
    - Requiere: rol de Administrador
    - No se elimina f├¡sicamente, solo se desactiva
    """
    verificar_es_admin(usuario_actual)
    
    try:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # No permitir eliminar al propio administrador
        if usuario.id_usuario == usuario_actual.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propia cuenta"
            )
        
        # Desactivar usuario
        usuario.activo = False
        db.commit()
        
        # Registrar auditor├¡a
        registrar_auditoria(
            db=db,
            usuario_id=usuario_actual.id_usuario,
            accion="ELIMINAR_USUARIO",
            detalles=f"Usuario desactivado: {usuario.email} (ID: {usuario.id_usuario})"
        )
        
        logger.info(f"Usuario {usuario_id} desactivado por admin ID: {usuario_actual.id_usuario}")
        
        return {"message": f"Usuario {usuario.email} desactivado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar usuario"
        )


@router.patch("/{usuario_id}/activar")
async def activar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Reactivar un usuario desactivado
    - Requiere: rol de Administrador
    - Cambia el estado de activo=False a activo=True
    """
    verificar_es_admin(usuario_actual)
    
    try:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        if usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya est├í activo"
            )
        
        # Reactivar usuario
        usuario.activo = True
        db.commit()
        
        # Registrar auditor├¡a
        registrar_auditoria(
            db=db,
            usuario_id=usuario_actual.id_usuario,
            accion="ACTIVAR_USUARIO",
            detalles=f"Usuario reactivado: {usuario.email} (ID: {usuario.id_usuario})"
        )
        
        logger.info(f"Usuario {usuario_id} reactivado por admin ID: {usuario_actual.id_usuario}")
        
        return {"message": f"Usuario {usuario.email} reactivado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al reactivar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al reactivar usuario"
        )


@router.get("/roles/listar")
async def listar_roles(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Listar todos los roles disponibles
    - Requiere: rol de Administrador
    """
    verificar_es_admin(usuario_actual)
    
    roles = db.query(Rol).all()
    
    return [
        {
            "id_rol": rol.id_rol,
            "nombre": rol.nombre,
            "descripcion": rol.descripcion
        }
        for rol in roles
    ]