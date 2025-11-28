"""
Router de Autenticación - Endpoints de login, register, logout, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.dto.auth_dtos import (
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    TokenRefreshRequest, TokenRefreshResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    UsuarioResponse, LogoutResponse
)
from app.entities.user_entity import Usuario, Rol, Auditoria
from app.utils.jwt_utils import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    decode_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, Roles
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
    ip_address: str,
    user_agent: str,
    exitoso: bool,
    mensaje: Optional[str] = None
):
    """Registrar evento en auditoría"""
    try:
        auditoria = AuditoriaAccesoDB(
            usuario_id=usuario_id,
            accion=accion,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje=mensaje
        )
        db.add(auditoria)
        db.commit()
    except Exception as e:
        logger.error(f"Error al registrar auditoría: {e}")
        db.rollback()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Registrar un nuevo usuario en el sistema"""
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(UsuarioDB).filter(
            (UsuarioDB.username == data.username.lower()) | (UsuarioDB.email == data.email.lower())
        ).first()
        
        if existing_user:
            if existing_user.username == data.username.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está registrado"
                )
        
        # Crear nuevo usuario
        nuevo_usuario = UsuarioDB(
            username=data.username.lower(),
            email=data.email.lower(),
            password_hash=get_password_hash(data.password),
            nombre=data.nombre,
            apellido=data.apellido,
            rol='usuario',
            estado=True
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        # Crear perfil vacío
        nuevo_perfil = PerfilDB(usuario_id=nuevo_usuario.id)
        db.add(nuevo_perfil)
        db.commit()
        
        # Registrar en auditoría
        registrar_auditoria(
            db=db,
            usuario_id=nuevo_usuario.id,
            accion="REGISTRO",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            exitoso=True,
            mensaje=f"Usuario {nuevo_usuario.username} registrado exitosamente"
        )
        
        logger.info(f"Usuario registrado exitosamente: {nuevo_usuario.username}")
        
        return RegisterResponse(
            id=nuevo_usuario.id,
            username=nuevo_usuario.username,
            email=nuevo_usuario.email,
            nombre=nuevo_usuario.nombre,
            apellido=nuevo_usuario.apellido,
            rol=nuevo_usuario.rol
        )
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al registrar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar usuario"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al registrar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Iniciar sesión en el sistema"""
    try:
        # Buscar usuario
        usuario = db.query(UsuarioDB).filter(
            UsuarioDB.username == data.username.lower()
        ).first()
        
        # Verificar usuario y contraseña
        if not usuario or not verify_password(data.password, usuario.password_hash):
            registrar_auditoria(
                db=db,
                usuario_id=usuario.id if usuario else None,
                accion="LOGIN_FALLIDO",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                exitoso=False,
                mensaje=f"Intento de login fallido para usuario: {data.username}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        # Verificar que el usuario esté activo
        if not usuario.estado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario desactivado"
            )
        
        # Crear tokens
        token_data = {
            "sub": usuario.username,
            "user_id": usuario.id,
            "rol": usuario.rol
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Guardar sesión
        nueva_sesion = SesionDB(
            usuario_id=usuario.id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            fecha_expiracion=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            activo=True
        )
        db.add(nueva_sesion)
        
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        db.commit()
        
        # Registrar login exitoso
        registrar_auditoria(
            db=db,
            usuario_id=usuario.id,
            accion="LOGIN",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            exitoso=True,
            mensaje=f"Login exitoso para usuario: {usuario.username}"
        )
        
        logger.info(f"Login exitoso: {usuario.username}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            usuario=UsuarioResponse.from_orm(usuario)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refrescar el access token usando un refresh token válido"""
    try:
        payload = decode_token(data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido"
            )
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        # Verificar sesión activa
        sesion = db.query(SesionDB).filter(
            SesionDB.refresh_token == data.refresh_token,
            SesionDB.activo == True
        ).first()
        
        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión inválida o expirada"
            )
        
        # Verificar usuario activo
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == user_id).first()
        if not usuario or not usuario.estado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Crear nuevo access token
        token_data = {
            "sub": username,
            "user_id": user_id,
            "rol": usuario.rol
        }
        
        new_access_token = create_access_token(token_data)
        
        # Actualizar sesión
        sesion.token = new_access_token
        sesion.fecha_expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        db.commit()
        
        logger.info(f"Token refrescado para usuario: {username}")
        
        return TokenRefreshResponse(
            access_token=new_access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al refrescar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cerrar sesión del usuario actual"""
    try:
        user_id = current_user["user_id"]
        
        # Desactivar todas las sesiones del usuario
        db.query(SesionDB).filter(
            SesionDB.usuario_id == user_id,
            SesionDB.activo == True
        ).update({"activo": False})
        
        db.commit()
        
        logger.info(f"Logout exitoso: {current_user['username']}")
        
        return LogoutResponse(message="Sesión cerrada exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesión"
        )


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener información del usuario actual autenticado"""
    try:
        usuario = db.query(UsuarioDB).filter(
            UsuarioDB.id == current_user["user_id"]
        ).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return UsuarioResponse.from_orm(usuario)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener información del usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar la contraseña del usuario actual"""
    try:
        usuario = db.query(UsuarioDB).filter(
            UsuarioDB.id == current_user["user_id"]
        ).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(data.password_actual, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Actualizar contraseña
        usuario.password_hash = get_password_hash(data.password_nueva)
        usuario.fecha_actualizacion = datetime.utcnow()
        
        # Invalidar todas las sesiones
        db.query(SesionDB).filter(
            SesionDB.usuario_id == usuario.id,
            SesionDB.activo == True
        ).update({"activo": False})
        
        db.commit()
        
        logger.info(f"Contraseña cambiada para usuario: {usuario.username}")
        
        return ChangePasswordResponse(
            message="Contraseña actualizada exitosamente. Por favor, inicia sesión nuevamente."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al cambiar contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
