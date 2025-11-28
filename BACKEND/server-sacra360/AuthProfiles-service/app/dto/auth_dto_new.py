"""
DTOs para autenticación usando la estructura de BD existente
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date

# ============ LOGIN ============

class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr = Field(..., description="Email del usuario")
    contrasenia: str = Field(..., min_length=6, description="Contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@sacra360.com",
                "contrasenia": "admin123"
            }
        }


class UsuarioResponse(BaseModel):
    """Response con información del usuario"""
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    rol_id: int
    nombre_rol: Optional[str] = None
    activo: bool
    fecha_creacion: date
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response del login con token y usuario"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
    usuario: UsuarioResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "usuario": {
                    "id_usuario": 1,
                    "nombre": "Admin",
                    "apellido_paterno": "Sistema",
                    "apellido_materno": "Principal",
                    "email": "admin@sacra360.com",
                    "rol_id": 1,
                    "nombre_rol": "Administrador",
                    "activo": True,
                    "fecha_creacion": "2024-01-01"
                }
            }
        }


# ============ REGISTER ============

class RegisterRequest(BaseModel):
    """Request para registro de nuevo usuario"""
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido_paterno: str = Field(..., min_length=2, max_length=50)
    apellido_materno: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    contrasenia: str = Field(..., min_length=6, description="Mínimo 6 caracteres")
    contrasenia_confirmacion: str = Field(..., min_length=6)
    rol_id: int = Field(default=4, description="ID del rol (default: usuario)")
    
    @validator('contrasenia_confirmacion')
    def passwords_match(cls, v, values):
        if 'contrasenia' in values and v != values['contrasenia']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan",
                "apellido_paterno": "Pérez",
                "apellido_materno": "García",
                "email": "juan.perez@example.com",
                "contrasenia": "password123",
                "contrasenia_confirmacion": "password123",
                "rol_id": 4
            }
        }


class RegisterResponse(BaseModel):
    """Response del registro exitoso"""
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    rol_id: int
    message: str = "Usuario registrado exitosamente"
    
    class Config:
        from_attributes = True


# ============ CHANGE PASSWORD ============

class ChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña"""
    contrasenia_actual: str = Field(..., min_length=6)
    contrasenia_nueva: str = Field(..., min_length=6)
    contrasenia_confirmacion: str = Field(..., min_length=6)
    
    @validator('contrasenia_confirmacion')
    def passwords_match(cls, v, values):
        if 'contrasenia_nueva' in values and v != values['contrasenia_nueva']:
            raise ValueError('Las contraseñas nuevas no coinciden')
        return v


# ============ TOKEN ============

class TokenData(BaseModel):
    """Datos contenidos en el token JWT"""
    email: Optional[str] = None
    id_usuario: Optional[int] = None
    rol_id: Optional[int] = None


# ============ USER UPDATE ============

class UserUpdateRequest(BaseModel):
    """Request para actualizar datos del usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido_paterno: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido_materno: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Carlos",
                "apellido_paterno": "Pérez",
                "email": "nuevoemail@example.com"
            }
        }


#  ============ LEGACY DTOs (mantener compatibilidad) ============

from enum import Enum

class UserRole(str, Enum):
    """Enum de roles de usuario"""
    ARCHBISHOP = "archbishop"  
    BISHOP = "bishop"
    PRIEST = "priest"
    DEACON = "deacon"
    ADMIN = "admin"
    DIGITIZER = "digitizer"
    VIEWER = "viewer"
