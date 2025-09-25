"""
Endpoints para gestión de usuarios del Sistema Sacra360
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import timedelta

from ..schemas.sacra360_schemas import (
    UsuarioCreate, UsuarioResponse, UsuarioUpdate, 
    LoginRequest, Token, MessageResponse, PaginationParams,
    RolResponse
)
from ..core.security import SecurityManager
from ..core.config import settings

# Configuración del router
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
security = HTTPBearer()

# Simulación de base de datos en memoria (reemplazar con tu ORM)
fake_usuarios_db = {
    1: {
        "id_usuario": 1,
        "nombre": "Administrador",
        "apellido_paterno": "Sistema",
        "apellido_materno": "Sacra360",
        "email": "admin@sacra360.com",
        "password": SecurityManager.get_password_hash("Admin123!"),
        "id_rol": 1,
        "rol": "admin",
        "activo": True,
        "fecha_creacion": "2025-09-25T00:00:00"
    }
}
fake_roles_db = {
    1: {"id_rol": 1, "rol": "admin", "descripcion": "Administrador del sistema"},
    2: {"id_rol": 2, "rol": "sacerdote", "descripcion": "Sacerdote de la parroquia"},
    3: {"id_rol": 3, "rol": "secretario", "descripcion": "Secretario parroquial"},
    4: {"id_rol": 4, "rol": "consultor", "descripcion": "Consultor de registros"}
}
usuario_id_counter = 2


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Obtiene el usuario actual desde el token JWT"""
    try:
        payload = SecurityManager.verify_token(credentials.credentials)
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Buscar el usuario en la "base de datos"
        usuario = fake_usuarios_db.get(user_id)
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return usuario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Verifica que el usuario actual sea administrador"""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UsuarioCreate,
    admin_user: dict = Depends(get_admin_user)  # Solo admin puede registrar usuarios
):
    """
    Registra un nuevo usuario en el sistema Sacra360.
    
    Solo los administradores pueden registrar nuevos usuarios.
    
    - **nombre**: Nombre del usuario (requerido)
    - **apellido_paterno**: Apellido paterno
    - **apellido_materno**: Apellido materno
    - **email**: Email único del usuario
    - **password**: Contraseña segura
    - **id_rol**: ID del rol asignado
    """
    global usuario_id_counter
    
    # Verificar si el email ya existe
    for usuario in fake_usuarios_db.values():
        if usuario["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este email"
            )
    
    # Verificar que el rol existe
    if user_data.id_rol not in fake_roles_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol especificado no existe"
        )
    
    # Verificar que las contraseñas coinciden
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden"
        )
    
    # Crear el usuario
    hashed_password = SecurityManager.get_password_hash(user_data.password)
    
    nuevo_usuario = {
        "id_usuario": usuario_id_counter,
        "nombre": user_data.nombre,
        "apellido_paterno": user_data.apellido_paterno,
        "apellido_materno": user_data.apellido_materno,
        "email": user_data.email,
        "fecha_nacimiento": user_data.fecha_nacimiento,
        "activo": user_data.activo,
        "id_rol": user_data.id_rol,
        "rol": fake_roles_db[user_data.id_rol]["rol"],
        "password": hashed_password
    }
    
    fake_usuarios_db[usuario_id_counter] = nuevo_usuario
    usuario_id_counter += 1
    
    # Preparar respuesta sin contraseña
    response_user = {k: v for k, v in nuevo_usuario.items() if k != "password"}
    response_user["rol"] = RolResponse(**fake_roles_db[user_data.id_rol])
    
    return UsuarioResponse(**response_user)


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Autentica un usuario en el sistema Sacra360.
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    """
    # Buscar usuario por email
    usuario = None
    for u in fake_usuarios_db.values():
        if u["email"] == login_data.email:
            usuario = u
            break
    
    if not usuario or not SecurityManager.verify_password(login_data.password, usuario["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not usuario["activo"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = SecurityManager.create_access_token(
        data={"sub": usuario["email"], "user_id": usuario["id_usuario"]},
        expires_delta=access_token_expires
    )
    
    # Preparar información del usuario
    user_info = {k: v for k, v in usuario.items() if k != "password"}
    user_info["rol"] = RolResponse(**fake_roles_db[usuario["id_rol"]])
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user_info=UsuarioResponse(**user_info)
    )


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtiene la información del usuario autenticado.
    """
    response_user = {k: v for k, v in current_user.items() if k != "password"}
    response_user["rol"] = RolResponse(**fake_roles_db[current_user["id_rol"]])
    return UsuarioResponse(**response_user)


@router.get("/", response_model=List[UsuarioResponse])
async def get_users(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    id_rol: Optional[int] = Query(None, description="Filtrar por rol"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de usuarios.
    
    Requiere autenticación. Los usuarios pueden ver información limitada.
    """
    # Filtrar usuarios
    filtered_users = list(fake_usuarios_db.values())
    
    if search:
        search_lower = search.lower()
        filtered_users = [
            u for u in filtered_users 
            if (search_lower in u["nombre"].lower() or 
                search_lower in u["email"].lower() or
                (u["apellido_paterno"] and search_lower in u["apellido_paterno"].lower()) or
                (u["apellido_materno"] and search_lower in u["apellido_materno"].lower()))
        ]
    
    if activo is not None:
        filtered_users = [u for u in filtered_users if u["activo"] == activo]
        
    if id_rol is not None:
        filtered_users = [u for u in filtered_users if u["id_rol"] == id_rol]
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_users = filtered_users[start:end]
    
    # Preparar respuesta sin contraseñas y con información de roles
    clean_users = []
    for user in paginated_users:
        clean_user = {k: v for k, v in user.items() if k != "password"}
        clean_user["rol"] = RolResponse(**fake_roles_db[user["id_rol"]])
        clean_users.append(UsuarioResponse(**clean_user))
    
    return clean_users


@router.get("/{user_id}", response_model=UsuarioResponse)
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un usuario por su ID.
    
    Los usuarios pueden ver su propia información completa.
    Otros usuarios ven información limitada.
    """
    usuario = fake_usuarios_db.get(user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    response_user = {k: v for k, v in usuario.items() if k != "password"}
    response_user["rol"] = RolResponse(**fake_roles_db[usuario["id_rol"]])
    return UsuarioResponse(**response_user)


@router.put("/{user_id}", response_model=UsuarioResponse)
async def update_user(
    user_id: int,
    user_update: UsuarioUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza la información de un usuario.
    
    Los usuarios pueden actualizar su propia información (limitada).
    Los administradores pueden actualizar cualquier usuario.
    """
    usuario = fake_usuarios_db.get(user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar permisos
    is_admin = current_user.get("rol") == "admin"
    is_own_profile = current_user["id_usuario"] == user_id
    
    if not is_admin and not is_own_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    # Obtener datos a actualizar
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Si no es admin, limitar campos que puede modificar
    if not is_admin:
        allowed_fields = {"nombre", "apellido_paterno", "apellido_materno", "fecha_nacimiento"}
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    # Verificar unicidad de email si se está actualizando
    if "email" in update_data:
        for uid, u in fake_usuarios_db.items():
            if uid != user_id and u["email"] == update_data["email"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está en uso"
                )
    
    # Verificar que el rol existe si se está actualizando
    if "id_rol" in update_data and update_data["id_rol"] not in fake_roles_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol especificado no existe"
        )
    
    # Actualizar campos
    for field, value in update_data.items():
        usuario[field] = value
    
    # Actualizar rol en el diccionario si cambió
    if "id_rol" in update_data:
        usuario["rol"] = fake_roles_db[update_data["id_rol"]]["rol"]
    
    response_user = {k: v for k, v in usuario.items() if k != "password"}
    response_user["rol"] = RolResponse(**fake_roles_db[usuario["id_rol"]])
    return UsuarioResponse(**response_user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    admin_user: dict = Depends(get_admin_user)  # Solo admin puede eliminar
):
    """
    Elimina un usuario del sistema.
    
    Solo los administradores pueden eliminar usuarios.
    No se puede eliminar a sí mismo.
    """
    if user_id not in fake_usuarios_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir que un admin se elimine a sí mismo
    if user_id == admin_user["id_usuario"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo"
        )
    
    # En lugar de eliminar, desactivar el usuario (mejor práctica)
    fake_usuarios_db[user_id]["activo"] = False
    
    return MessageResponse(
        message="Usuario desactivado exitosamente",
        success=True
    )


@router.patch("/{user_id}/toggle-status", response_model=UsuarioResponse)
async def toggle_user_status(
    user_id: int,
    admin_user: dict = Depends(get_admin_user)
):
    """
    Activa o desactiva un usuario.
    
    Solo los administradores pueden cambiar el estado de los usuarios.
    """
    usuario = fake_usuarios_db.get(user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Cambiar estado
    usuario["activo"] = not usuario["activo"]
    
    response_user = {k: v for k, v in usuario.items() if k != "password"}
    response_user["rol"] = RolResponse(**fake_roles_db[usuario["id_rol"]])
    
    return UsuarioResponse(**response_user)


@router.post("/setup-admin", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def setup_first_admin(user_data: UsuarioCreate):
    """
    Endpoint especial para configurar el primer administrador.
    
    Solo funciona si no hay usuarios administradores en el sistema.
    Este endpoint es público y no requiere autenticación.
    """
    global usuario_id_counter
    
    # Verificar si ya existe un administrador
    admin_exists = any(
        usuario.get("rol") == "admin" and usuario.get("activo", False)
        for usuario in fake_usuarios_db.values()
    )
    
    if admin_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ya existe un administrador en el sistema. Use el endpoint de registro normal."
        )
    
    # Verificar si el email ya existe
    for usuario in fake_usuarios_db.values():
        if usuario["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este email"
            )
    
    # Crear el primer administrador
    nuevo_usuario = {
        "id_usuario": usuario_id_counter,
        "nombre": user_data.nombre,
        "apellido_paterno": user_data.apellido_paterno,
        "apellido_materno": user_data.apellido_materno,
        "email": user_data.email,
        "password": SecurityManager.get_password_hash(user_data.password),
        "id_rol": 1,  # Forzar rol de admin
        "rol": "admin",
        "activo": True,
        "fecha_creacion": "2025-09-25T00:00:00"
    }
    
    fake_usuarios_db[usuario_id_counter] = nuevo_usuario
    usuario_id_counter += 1
    
    # Preparar respuesta
    response_user = {k: v for k, v in nuevo_usuario.items() if k != "password"}
    response_user["rol"] = RolResponse(**fake_roles_db[1])
    
    return UsuarioResponse(**response_user)