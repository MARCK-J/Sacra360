"""
Data Transfer Objects para Authentication y Profiles
Validación de datos con Pydantic
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums para roles eclesiásticos
class UserRole(str, Enum):
    ARCHBISHOP = "archbishop"        # Arzobispo
    BISHOP = "bishop"               # Obispo  
    PRIEST = "priest"               # Sacerdote
    DEACON = "deacon"               # Diácono
    ADMINISTRATOR = "administrator"  # Administrativo
    ARCHIVIST = "archivist"         # Archivista
    VIEWER = "viewer"               # Solo lectura


class Parish(str, Enum):
    CATHEDRAL = "cathedral"         # Catedral
    PARISH = "parish"              # Parroquia
    CHAPEL = "chapel"              # Capilla
    SEMINARY = "seminary"          # Seminario


# DTOs de Autenticación
class LoginRequest(BaseModel):
    """Solicitud de login"""
    email: EmailStr
    password: str = None
    contrasenia: str = None  # Alias temporal para compatibilidad
    remember_me: bool = False

    @property
    def get_password(self):
        """Obtener contraseña de cualquier campo"""
        return self.password or self.contrasenia

    class Config:
        json_schema_extra = {
            "example": {
                "email": "padre.juan@arzobispado.org",
                "password": "mi_password_seguro",
                "remember_me": False
            }
        }


class LoginResponse(BaseModel):
    """Respuesta de login exitoso"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict
    permissions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_info": {
                    "id": "123",
                    "email": "padre.juan@arzobispado.org",
                    "full_name": "P. Juan Pérez"
                },
                "permissions": ["documents:read", "documents:write"]
            }
        }


class RegisterRequest(BaseModel):
    """Solicitud de registro de nuevo usuario"""
    email: EmailStr
    password: str
    confirm_password: str
    full_name: str
    role: UserRole
    parish_assignment: Optional[str] = None
    phone: Optional[str] = None
    ordination_date: Optional[datetime] = None

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "nuevo.sacerdote@arzobispado.org",
                "password": "MiPassword123",
                "confirm_password": "MiPassword123",
                "full_name": "P. Nuevo Sacerdote",
                "role": "priest",
                "parish_assignment": "Parroquia San José",
                "phone": "+57 300 123 4567",
                "ordination_date": "2020-06-29T00:00:00"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Solicitud de cambio de contraseña"""
    current_password: str
    new_password: str
    confirm_new_password: str

    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas nuevas no coinciden')
        return v


# DTOs de Perfiles
class ProfileResponse(BaseModel):
    """Respuesta con información del perfil"""
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    parish_assignment: Optional[str] = None
    phone: Optional[str] = None
    ordination_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    permissions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user123",
                "email": "padre.juan@arzobispado.org",
                "full_name": "P. Juan Pérez",
                "role": "priest",
                "parish_assignment": "Parroquia San José",
                "phone": "+57 300 123 4567",
                "ordination_date": "2015-06-29T00:00:00",
                "is_active": True,
                "created_at": "2023-01-15T10:30:00",
                "last_login": "2024-10-09T08:15:00",
                "permissions": ["documents:read", "documents:write", "sacraments:baptism"]
            }
        }


class UpdateProfileRequest(BaseModel):
    """Solicitud de actualización de perfil"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    parish_assignment: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "P. Juan Pérez González",
                "phone": "+57 300 987 6543",
                "parish_assignment": "Catedral Primada"
            }
        }


class PermissionRequest(BaseModel):
    """Solicitud de gestión de permisos"""
    user_id: str
    permissions: List[str]
    action: str  # "grant" o "revoke"

    @validator('action')
    def validate_action(cls, v):
        if v not in ['grant', 'revoke']:
            raise ValueError('La acción debe ser "grant" o "revoke"')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "permissions": ["documents:write", "sacraments:marriage"],
                "action": "grant"
            }
        }


# DTOs de respuesta general
class SuccessResponse(BaseModel):
    """Respuesta de operación exitosa"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# DTOs para listados
class UserListResponse(BaseModel):
    """Respuesta con lista de usuarios"""
    users: List[ProfileResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_previous: bool


# DTOs para tokens
class TokenValidationRequest(BaseModel):
    """Solicitud de validación de token"""
    token: str


class TokenValidationResponse(BaseModel):
    """Respuesta de validación de token"""
    valid: bool
    user_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    permissions: Optional[List[str]] = None


class RegisterResponse(BaseModel):
    """Respuesta de registro exitoso"""
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    email: str
    rol_id: int
    nombre_rol: str
    activo: bool
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class UsuarioResponse(BaseModel):
    """Respuesta con información del usuario"""
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    email: str
    rol_id: int
    nombre_rol: str
    activo: bool
    fecha_creacion: datetime
    ultima_sesion: Optional[datetime] = None
    
    class Config:
        from_attributes = True