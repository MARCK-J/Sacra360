"""
DTOs para Autenticación y Gestión de Usuarios
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# ============= Login =============
class LoginRequest(BaseModel):
    """Request para login"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    password: str = Field(..., min_length=6, description="Contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class LoginResponse(BaseModel):
    """Response del login exitoso"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: "UsuarioResponse"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "usuario": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@sacra360.com",
                    "nombre": "Administrador",
                    "apellido": "Sistema",
                    "rol": "administrador"
                }
            }
        }


# ============= Register =============
class RegisterRequest(BaseModel):
    """Request para registro de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validar que el username solo contenga caracteres permitidos"""
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        """Validar fortaleza de la contraseña"""
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "juan.perez",
                "email": "juan.perez@sacra360.com",
                "password": "Password123!",
                "nombre": "Juan",
                "apellido": "Pérez"
            }
        }


class RegisterResponse(BaseModel):
    """Response del registro exitoso"""
    id: int
    username: str
    email: str
    nombre: str
    apellido: str
    rol: str
    message: str = "Usuario registrado exitosamente"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 2,
                "username": "juan.perez",
                "email": "juan.perez@sacra360.com",
                "nombre": "Juan",
                "apellido": "Pérez",
                "rol": "usuario",
                "message": "Usuario registrado exitosamente"
            }
        }


# ============= Usuario Response =============
class UsuarioResponse(BaseModel):
    """Response de información del usuario"""
    id: int
    username: str
    email: str
    nombre: str
    apellido: str
    rol: str
    estado: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@sacra360.com",
                "nombre": "Administrador",
                "apellido": "Sistema",
                "rol": "administrador",
                "estado": True,
                "fecha_creacion": "2024-01-01T00:00:00",
                "ultimo_acceso": "2024-11-27T18:00:00"
            }
        }


# ============= Perfil =============
class PerfilUpdate(BaseModel):
    """Request para actualizar perfil"""
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = None
    foto_perfil: Optional[str] = None
    biografia: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    genero: Optional[str] = Field(None, pattern="^(masculino|femenino|otro)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "telefono": "+57 300 123 4567",
                "direccion": "Calle 123 #45-67, Bogotá",
                "biografia": "Digitalizador de registros parroquiales",
                "genero": "masculino"
            }
        }


class PerfilResponse(BaseModel):
    """Response del perfil del usuario"""
    id: int
    usuario_id: int
    telefono: Optional[str]
    direccion: Optional[str]
    foto_perfil: Optional[str]
    biografia: Optional[str]
    fecha_nacimiento: Optional[datetime]
    genero: Optional[str]
    
    class Config:
        from_attributes = True


# ============= Token Refresh =============
class TokenRefreshRequest(BaseModel):
    """Request para refrescar token"""
    refresh_token: str = Field(..., description="Refresh token obtenido en el login")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenRefreshResponse(BaseModel):
    """Response con nuevo access token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


# ============= Change Password =============
class ChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña"""
    password_actual: str = Field(..., description="Contraseña actual")
    password_nueva: str = Field(..., min_length=6, description="Nueva contraseña")
    password_confirmacion: str = Field(..., description="Confirmación de nueva contraseña")
    
    @validator('password_confirmacion')
    def passwords_match(cls, v, values):
        """Validar que las contraseñas coincidan"""
        if 'password_nueva' in values and v != values['password_nueva']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "password_actual": "Password123!",
                "password_nueva": "NuevaPassword456!",
                "password_confirmacion": "NuevaPassword456!"
            }
        }


class ChangePasswordResponse(BaseModel):
    """Response del cambio de contraseña"""
    message: str = "Contraseña actualizada exitosamente"


# ============= Logout =============
class LogoutResponse(BaseModel):
    """Response del logout"""
    message: str = "Sesión cerrada exitosamente"
