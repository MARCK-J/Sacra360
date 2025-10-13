from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Enums para valores predefinidos
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


# Schemas base
class BaseSchema(BaseModel):
    """Schema base con configuración común"""
    
    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True
    }


# Schemas de Usuario
class UserBase(BaseSchema):
    """Schema base para usuario"""
    email: str = Field(..., description="Email del usuario")
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo")
    is_active: bool = Field(True, description="Usuario activo")
    role: UserRole = Field(UserRole.USER, description="Rol del usuario")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras, números y guiones bajos')
        return v.lower()


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña del usuario")
    confirm_password: str = Field(..., description="Confirmación de contraseña")
    
    # Validador de contraseñas - se validará en el endpoint
    # @field_validator('confirm_password')
    # @classmethod
    # def passwords_match(cls, v, info):
    #     return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe tener al menos una mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe tener al menos una minúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe tener al menos un número')
        return v


class UserUpdate(BaseSchema):
    """Schema para actualizar usuario"""
    email: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """Schema para respuesta de usuario"""
    id: int = Field(..., description="ID único del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")


class UserList(BaseSchema):
    """Schema para lista de usuarios"""
    users: List[UserResponse]
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Límite por página")


# Schemas de Autenticación
class Token(BaseSchema):
    """Schema para token de acceso"""
    access_token: str = Field(..., description="Token de acceso")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")


class TokenData(BaseSchema):
    """Schema para datos del token"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseSchema):
    """Schema para solicitud de login"""
    username: str = Field(..., description="Nombre de usuario o email")
    password: str = Field(..., description="Contraseña")


# Schemas de respuesta general
class MessageResponse(BaseSchema):
    """Schema para respuestas con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(True, description="Indica si la operación fue exitosa")


class ErrorResponse(BaseSchema):
    """Schema para respuestas de error"""
    error: str = Field(..., description="Descripción del error")
    detail: Optional[str] = Field(None, description="Detalle adicional del error")
    code: Optional[str] = Field(None, description="Código de error")


# Schemas para paginación
class PaginationParams(BaseSchema):
    """Schema para parámetros de paginación"""
    page: int = Field(1, ge=1, description="Número de página")
    limit: int = Field(10, ge=1, le=100, description="Límite de elementos por página")
    sort_by: Optional[str] = Field("id", description="Campo por el cual ordenar")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Orden ascendente o descendente")


# Schemas de ejemplo para otros recursos (puedes adaptarlos según tu dominio)
class ResourceBase(BaseSchema):
    """Schema base para recursos generales"""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del recurso")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción del recurso")
    status: StatusEnum = Field(StatusEnum.ACTIVE, description="Estado del recurso")


class ResourceCreate(ResourceBase):
    """Schema para crear recurso"""
    pass


class ResourceUpdate(BaseSchema):
    """Schema para actualizar recurso"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[StatusEnum] = None


class ResourceResponse(ResourceBase):
    """Schema para respuesta de recurso"""
    id: int = Field(..., description="ID único del recurso")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    created_by: int = Field(..., description="ID del usuario que creó el recurso")