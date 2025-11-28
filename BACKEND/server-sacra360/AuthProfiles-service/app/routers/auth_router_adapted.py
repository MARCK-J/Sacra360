"""
Router de Autenticación adaptado a la BD existente de Sacra360
Endpoints: login, register, logout, cambiar contraseña, obtener usuario actual
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Optional
import logging

# Importar DTOs nuevos
from app.dto.auth_dto_new import (
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    ChangePasswordRequest,
    UsuarioResponse
)

# Importar entidades
from app.entities.user_entity import Usuario, Rol, Auditoria

# Importar utilidades
from app.utils.auth_utils import (
    verify_password, get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


# Dependency para obtener la sesión de BD
def get_db():
    """Dependency para obtener la sesión de base de datos"""
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
            registro_afectado="AUTH",
            id_registro=usuario_id if usuario_id else 0,
            fecha=datetime.now()
        )
        db.add(auditoria)
        db.commit()
        logger.info(f"Auditoría registrada: {accion} - Usuario: {usuario_id}")
    except Exception as e:
        logger.error(f"Error al registrar auditoría: {e}")
        db.rollback()


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión en el sistema
    
    Returns:
        Token de acceso y datos del usuario
    """
    try:
        # Buscar usuario por email
        usuario = db.query(Usuario).filter(Usuario.email == data.email.lower()).first()
        
        # Verificar que el usuario existe y la contraseña es correcta
        if not usuario or not verify_password(data.contrasenia, usuario.contrasenia):
            # Registrar intento fallido
            if usuario:
                try:
                    registrar_auditoria(
                        db=db,
                        usuario_id=usuario.id_usuario,
                        accion="LOGIN_FALLIDO",
                        detalles=f"Intento de login fallido para email: {data.email}"
                    )
                except:
                    pass  # No fallar si no se puede registrar auditoría
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Verificar que el usuario esté activo
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario desactivado. Contacte al administrador."
            )
        
        # Obtener información del rol
        rol = db.query(Rol).filter(Rol.id_rol == usuario.rol_id).first()
        nombre_rol = rol.nombre if rol else "Sin rol"
        
        # Crear token JWT
        token_data = {
            "sub": usuario.email,
            "id_usuario": usuario.id_usuario,
            "rol_id": usuario.rol_id,
            "nombre": usuario.nombre
        }
        
        access_token = create_access_token(token_data)
        
        # Registrar login exitoso
        registrar_auditoria(
            db=db,
            usuario_id=usuario.id_usuario,
            accion="LOGIN_EXITOSO",
            detalles=f"Login exitoso desde IP: {request.client.host}"
        )
        
        # Preparar response del usuario
        usuario_response = UsuarioResponse(
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
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            usuario=usuario_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo usuario en el sistema
    
    Returns:
        Datos del usuario creado
    """
    try:
        # Verificar si el email ya está registrado
        existing_user = db.query(Usuario).filter(Usuario.email == data.email.lower()).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado"
            )
        
        # Verificar que el rol existe
        rol = db.query(Rol).filter(Rol.id_rol == data.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El rol con ID {data.rol_id} no existe"
            )
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            rol_id=data.rol_id,
            nombre=data.nombre,
            apellido_paterno=data.apellido_paterno,
            apellido_materno=data.apellido_materno,
            email=data.email.lower(),
            contrasenia=get_password_hash(data.contrasenia),
            fecha_creacion=date.today(),
            activo=True
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        # Registrar en auditoría
        registrar_auditoria(
            db=db,
            usuario_id=nuevo_usuario.id_usuario,
            accion="REGISTRO_USUARIO",
            detalles=f"Nuevo usuario registrado: {nuevo_usuario.email}"
        )
        
        logger.info(f"Nuevo usuario registrado: {nuevo_usuario.email} (ID: {nuevo_usuario.id_usuario})")
        
        return RegisterResponse(
            id_usuario=nuevo_usuario.id_usuario,
            nombre=nuevo_usuario.nombre,
            apellido_paterno=nuevo_usuario.apellido_paterno,
            apellido_materno=nuevo_usuario.apellido_materno,
            email=nuevo_usuario.email,
            rol_id=nuevo_usuario.rol_id,
            message="Usuario registrado exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar usuario"
        )


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener información del usuario actualmente autenticado
    
    Returns:
        Datos completos del usuario
    """
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == current_user["id_usuario"]
        ).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener rol
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
        logger.error(f"Error obteniendo usuario actual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener información del usuario"
        )


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar la contraseña del usuario autenticado
    
    Returns:
        Mensaje de confirmación
    """
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == current_user["id_usuario"]
        ).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(data.contrasenia_actual, usuario.contrasenia):
            registrar_auditoria(
                db=db,
                usuario_id=usuario.id_usuario,
                accion="CAMBIO_CONTRASEÑA_FALLIDO",
                detalles="Contraseña actual incorrecta"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Actualizar contraseña
        usuario.contrasenia = get_password_hash(data.contrasenia_nueva)
        db.commit()
        
        # Registrar cambio exitoso
        registrar_auditoria(
            db=db,
            usuario_id=usuario.id_usuario,
            accion="CAMBIO_CONTRASEÑA_EXITOSO",
            detalles="Contraseña actualizada correctamente"
        )
        
        logger.info(f"Contraseña cambiada para usuario: {usuario.email}")
        
        return {
            "message": "Contraseña actualizada exitosamente",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cambiando contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar la contraseña"
        )


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cerrar sesión del usuario
    
    Returns:
        Mensaje de confirmación
    """
    try:
        # Registrar logout en auditoría
        registrar_auditoria(
            db=db,
            usuario_id=current_user["id_usuario"],
            accion="LOGOUT",
            detalles="Usuario cerró sesión"
        )
        
        logger.info(f"Logout exitoso para usuario ID: {current_user['id_usuario']}")
        
        return {
            "message": "Sesión cerrada exitosamente",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesión"
        )


@router.get("/roles")
async def get_roles(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de roles disponibles
    
    Returns:
        Lista de roles
    """
    try:
        roles = db.query(Rol).filter(Rol.activo == True).all()
        
        return {
            "roles": [
                {
                    "id_rol": rol.id_rol,
                    "nombre_rol": rol.nombre,
                    "descripcion": rol.descripcion
                }
                for rol in roles
            ]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener roles"
        )
