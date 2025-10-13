from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import timedelta

from ..schemas import (
    UserCreate, UserResponse, UserUpdate, UserList, 
    LoginRequest, Token, MessageResponse, PaginationParams
)
from ..core.security import SecurityManager
from ..core.config import settings

# Configuración del router
router = APIRouter(prefix="/users", tags=["Usuarios"])
security = HTTPBearer()

# Simulación de base de datos en memoria (reemplazar con tu ORM)
fake_users_db = {}
user_id_counter = 1


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Obtiene el usuario actual desde el token"""
    try:
        payload = SecurityManager.verify_token(credentials.credentials)
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Aquí deberías buscar el usuario en tu base de datos
        user = fake_users_db.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Registra un nuevo usuario en el sistema.
    
    - **email**: Email único del usuario
    - **username**: Nombre de usuario único
    - **password**: Contraseña (mínimo 8 caracteres, debe incluir mayúscula, minúscula y número)
    - **full_name**: Nombre completo (opcional)
    """
    global user_id_counter
    
    # Verificar si el usuario ya existe
    for user in fake_users_db.values():
        if user["email"] == user_data.email or user["username"] == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario o email ya existe"
            )
    
    # Crear el usuario
    hashed_password = SecurityManager.get_password_hash(user_data.password)
    
    new_user = {
        "id": user_id_counter,
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "is_active": user_data.is_active,
        "role": user_data.role,
        "hashed_password": hashed_password,
        "created_at": "2024-01-01T00:00:00",  # Reemplazar con datetime.utcnow()
        "updated_at": None
    }
    
    fake_users_db[user_id_counter] = new_user
    user_id_counter += 1
    
    # Remover la contraseña de la respuesta
    response_user = {k: v for k, v in new_user.items() if k != "hashed_password"}
    return UserResponse(**response_user)


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Autentica un usuario y devuelve un token de acceso.
    
    - **username**: Nombre de usuario o email
    - **password**: Contraseña del usuario
    """
    # Buscar usuario por username o email
    user = None
    for u in fake_users_db.values():
        if u["username"] == login_data.username or u["email"] == login_data.username:
            user = u
            break
    
    if not user or not SecurityManager.verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = SecurityManager.create_access_token(
        data={"sub": user["username"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtiene la información del usuario autenticado.
    """
    response_user = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return UserResponse(**response_user)


@router.get("/", response_model=UserList)
async def get_users(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre de usuario o email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de usuarios.
    
    Requiere autenticación. Solo administradores pueden ver todos los usuarios.
    """
    # Verificar permisos (solo admin puede ver lista completa)
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver la lista de usuarios"
        )
    
    # Filtrar usuarios
    filtered_users = list(fake_users_db.values())
    
    if search:
        filtered_users = [
            u for u in filtered_users 
            if search.lower() in u["username"].lower() or search.lower() in u["email"].lower()
        ]
    
    if is_active is not None:
        filtered_users = [u for u in filtered_users if u["is_active"] == is_active]
    
    # Paginación
    total = len(filtered_users)
    start = (page - 1) * limit
    end = start + limit
    paginated_users = filtered_users[start:end]
    
    # Remover contraseñas
    clean_users = [
        {k: v for k, v in user.items() if k != "hashed_password"}
        for user in paginated_users
    ]
    
    return UserList(
        users=[UserResponse(**user) for user in clean_users],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un usuario por su ID.
    
    Los usuarios solo pueden ver su propia información, excepto los administradores.
    """
    # Verificar permisos
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    response_user = {k: v for k, v in user.items() if k != "hashed_password"}
    return UserResponse(**response_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza la información de un usuario.
    
    Los usuarios solo pueden actualizar su propia información, excepto los administradores.
    """
    # Verificar permisos
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar unicidad de email y username si se están actualizando
    update_data = user_update.dict(exclude_unset=True)
    
    for field in ["email", "username"]:
        if field in update_data:
            for uid, u in fake_users_db.items():
                if uid != user_id and u[field] == update_data[field]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El {field} ya está en uso"
                    )
    
    # Actualizar campos
    for field, value in update_data.items():
        user[field] = value
    
    user["updated_at"] = "2024-01-01T00:00:00"  # Reemplazar con datetime.utcnow()
    
    response_user = {k: v for k, v in user.items() if k != "hashed_password"}
    return UserResponse(**response_user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un usuario del sistema.
    
    Solo los administradores pueden eliminar usuarios.
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar usuarios"
        )
    
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir que un admin se elimine a sí mismo
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo"
        )
    
    del fake_users_db[user_id]
    
    return MessageResponse(
        message="Usuario eliminado exitosamente",
        success=True
    )