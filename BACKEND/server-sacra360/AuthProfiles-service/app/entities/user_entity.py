"""
Entidades del dominio para Authentication y Profiles
Representación de datos del negocio
"""

<<<<<<< Updated upstream
<<<<<<< Updated upstream
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.dto.auth_dto import UserRole
=======
=======
>>>>>>> Stashed changes
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date

Base = declarative_base()
>>>>>>> Stashed changes


class UserEntity(BaseModel):
    """Entidad de usuario del sistema"""
    id: str
    email: EmailStr
    hashed_password: str
    full_name: str
    role: UserRole
    parish_assignment: Optional[str] = None
    phone: Optional[str] = None
    ordination_date: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None

    class Config:
        """Configuración de la entidad"""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "user_abc123",
                "email": "padre.juan@arzobispado.org",
                "hashed_password": "$2b$12$...",
                "full_name": "P. Juan Pérez",
                "role": "priest",
                "parish_assignment": "Parroquia San José",
                "phone": "+57 300 123 4567",
                "ordination_date": "2015-06-29T00:00:00",
                "is_active": True,
                "is_verified": True,
                "created_at": "2023-01-15T10:30:00",
                "last_login": "2024-10-09T08:15:00",
                "login_attempts": 0
            }
        }


class SessionEntity(BaseModel):
    """Entidad de sesión de usuario"""
    id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


<<<<<<< Updated upstream
class PermissionEntity(BaseModel):
    """Entidad de permisos del sistema"""
    id: str
    name: str
    description: str
    category: str  # documents, sacraments, users, reports
    resource: str  # specific resource within category
    action: str    # read, write, delete, admin

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "perm_001",
                "name": "documents:baptism:write",
                "description": "Escribir documentos de bautismo",
                "category": "documents",
                "resource": "baptism",
                "action": "write"
            }
        }


class UserPermissionEntity(BaseModel):
    """Entidad de relación usuario-permisos"""
    id: str
    user_id: str
    permission_id: str
    granted_at: datetime
    granted_by: str
    is_active: bool = True

    class Config:
        from_attributes = True


class RoleEntity(BaseModel):
    """Entidad de roles del sistema"""
    id: str
    name: UserRole
    description: str
    default_permissions: List[str]
    hierarchy_level: int  # 1=Archbishop, 2=Bishop, etc.
    can_manage_roles: List[UserRole]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "role_priest",
                "name": "priest",
                "description": "Sacerdote con acceso a documentos de su parroquia",
                "default_permissions": [
                    "documents:read",
                    "documents:write",
                    "sacraments:baptism",
                    "sacraments:marriage",
                    "sacraments:death"
                ],
                "hierarchy_level": 3,
                "can_manage_roles": ["deacon", "viewer"]
            }
        }


class ParishEntity(BaseModel):
    """Entidad de parroquia"""
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    diocese: str
    established_date: Optional[datetime] = None
    patron_saint: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "parish_001",
                "name": "Parroquia San José",
                "address": "Calle 15 # 23-45, Bogotá",
                "phone": "+57 1 234 5678",
                "email": "sanjose@arzobispado.org",
                "diocese": "Arquidiócesis de Bogotá",
                "established_date": "1950-03-19T00:00:00",
                "patron_saint": "San José",
                "is_active": True
            }
        }


class AuditLogEntity(BaseModel):
    """Entidad de auditoría de acciones"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    success: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "audit_001",
                "user_id": "user_abc123",
                "action": "login",
                "resource_type": "session",
                "details": {"login_method": "email_password"},
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "timestamp": "2024-10-09T08:15:00",
                "success": True
            }
        }
=======
class Auditoria(Base):
    """Entidad Auditoria para tracking de accesos"""
    __tablename__ = "auditoria"
    
    id_auditoria = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario'))
    accion = Column(Text, nullable=False)
    registro_afectado = Column(Text, nullable=False)
    id_registro = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="auditorias")
    
    def __repr__(self):
        return f"<Auditoria(id={self.id_auditoria}, accion={self.accion})>"
>>>>>>> Stashed changes
