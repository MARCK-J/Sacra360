"""
DTOs (Data Transfer Objects) para Documents Service
Modelos Pydantic para transferencia de datos de documentos sacramentales
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Tipos de documentos sacramentales"""
    BAPTISM = "baptism"
    CONFIRMATION = "confirmation"
    MARRIAGE = "marriage"
    DEATH = "death"
    ORDINATION = "ordination"
    FIRST_COMMUNION = "first_communion"
    CERTIFICATE = "certificate"
    PASTORAL_LETTER = "pastoral_letter"
    DECREE = "decree"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Estados de documentos"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    ACTIVE = "active"
    CANCELLED = "cancelled"


class SacramentType(str, Enum):
    """Tipos de sacramentos"""
    BAPTISM = "baptism"
    CONFIRMATION = "confirmation"
    EUCHARIST = "eucharist"
    PENANCE = "penance"
    ANOINTING = "anointing"
    HOLY_ORDERS = "holy_orders"
    MATRIMONY = "matrimony"


class MaritalStatus(str, Enum):
    """Estado civil"""
    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"
    DIVORCED = "divorced"
    SEPARATED = "separated"


# DTOs para Personas
class PersonDTO(BaseModel):
    """DTO para datos de persona"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    document_number: str = Field(..., min_length=5, max_length=20)
    document_type: str = Field(default="cedula")
    birth_date: datetime
    birth_place: str = Field(..., max_length=200)
    nationality: str = Field(default="Colombiana", max_length=100)
    gender: str = Field(..., regex="^(M|F|O)$")
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "Juan Carlos",
                "last_name": "Pérez González",
                "document_number": "12345678",
                "document_type": "cedula",
                "birth_date": "1990-05-15T00:00:00",
                "birth_place": "Bogotá, Colombia",
                "nationality": "Colombiana",
                "gender": "M"
            }
        }


class ParentsDTO(BaseModel):
    """DTO para datos de padres"""
    father_name: Optional[str] = Field(None, max_length=200)
    mother_name: Optional[str] = Field(None, max_length=200)
    father_document: Optional[str] = Field(None, max_length=20)
    mother_document: Optional[str] = Field(None, max_length=20)


# DTOs para Documentos
class CreateDocumentDTO(BaseModel):
    """DTO para crear documento"""
    document_type: DocumentType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    parish_id: str = Field(..., min_length=1)
    priest_id: str = Field(..., min_length=1)
    sacrament_type: Optional[SacramentType] = None
    participants: List[PersonDTO] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "document_type": "baptism",
                "title": "Certificado de Bautismo - Juan Carlos Pérez",
                "description": "Certificado de bautismo para Juan Carlos Pérez González",
                "parish_id": "parish_001",
                "priest_id": "priest_001",
                "sacrament_type": "baptism",
                "participants": [
                    {
                        "first_name": "Juan Carlos",
                        "last_name": "Pérez González",
                        "document_number": "12345678",
                        "document_type": "cedula",
                        "birth_date": "1990-05-15T00:00:00",
                        "birth_place": "Bogotá, Colombia",
                        "nationality": "Colombiana",
                        "gender": "M"
                    }
                ],
                "metadata": {
                    "book_number": "001",
                    "page_number": "125",
                    "record_number": "456"
                }
            }
        }


class DocumentDTO(BaseModel):
    """DTO para documento completo"""
    id: str
    document_type: DocumentType
    title: str
    description: Optional[str]
    status: DocumentStatus
    parish_id: str
    priest_id: str
    sacrament_type: Optional[SacramentType]
    participants: List[PersonDTO]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True


class UpdateDocumentDTO(BaseModel):
    """DTO para actualizar documento"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[DocumentStatus] = None
    participants: Optional[List[PersonDTO]] = None
    metadata: Optional[Dict[str, Any]] = None


# DTOs para Sacramentos específicos
class BaptismDTO(BaseModel):
    """DTO específico para bautismo"""
    person: PersonDTO
    parents: ParentsDTO
    godparents: Optional[List[PersonDTO]] = Field(default_factory=list)
    baptism_date: datetime
    parish_id: str
    priest_id: str
    book_number: str
    page_number: str
    record_number: str
    notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "person": {
                    "first_name": "Juan Carlos",
                    "last_name": "Pérez González",
                    "document_number": "12345678",
                    "document_type": "cedula",
                    "birth_date": "1990-05-15T00:00:00",
                    "birth_place": "Bogotá, Colombia",
                    "nationality": "Colombiana",
                    "gender": "M"
                },
                "parents": {
                    "father_name": "Carlos Pérez",
                    "mother_name": "María González",
                    "father_document": "87654321",
                    "mother_document": "98765432"
                },
                "godparents": [
                    {
                        "first_name": "Ana",
                        "last_name": "Rodríguez",
                        "document_number": "11223344",
                        "document_type": "cedula",
                        "birth_date": "1985-03-20T00:00:00",
                        "birth_place": "Medellín, Colombia",
                        "nationality": "Colombiana",
                        "gender": "F"
                    }
                ],
                "baptism_date": "2024-01-15T10:00:00",
                "parish_id": "parish_001",
                "priest_id": "priest_001",
                "book_number": "001",
                "page_number": "125",
                "record_number": "456",
                "notes": "Bautismo realizado durante la misa dominical"
            }
        }


class MarriageDTO(BaseModel):
    """DTO específico para matrimonio"""
    groom: PersonDTO
    bride: PersonDTO
    marriage_date: datetime
    parish_id: str
    priest_id: str
    witnesses: List[PersonDTO] = Field(default_factory=list)
    civil_marriage_date: Optional[datetime] = None
    civil_marriage_place: Optional[str] = None
    book_number: str
    page_number: str
    record_number: str
    notes: Optional[str] = None


class DeathDTO(BaseModel):
    """DTO específico para defunción"""
    person: PersonDTO
    death_date: datetime
    death_place: str
    death_cause: Optional[str] = None
    marital_status: MaritalStatus
    spouse_name: Optional[str] = None
    parish_id: str
    priest_id: str
    cemetery: Optional[str] = None
    burial_date: Optional[datetime] = None
    book_number: str
    page_number: str
    record_number: str
    notes: Optional[str] = None


# DTOs para consultas y filtros
class DocumentSearchDTO(BaseModel):
    """DTO para búsqueda de documentos"""
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    parish_id: Optional[str] = None
    priest_id: Optional[str] = None
    person_name: Optional[str] = None
    document_number: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class DocumentListResponseDTO(BaseModel):
    """DTO para respuesta de lista de documentos"""
    documents: List[DocumentDTO]
    total: int
    limit: int
    offset: int
    has_more: bool


# DTOs para estadísticas
class DocumentStatsDTO(BaseModel):
    """DTO para estadísticas de documentos"""
    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    documents_by_month: Dict[str, int]
    last_updated: datetime


# DTOs para respuestas de API
class DocumentResponseDTO(BaseModel):
    """DTO para respuesta de documento"""
    success: bool
    message: str
    data: Optional[DocumentDTO] = None


class DocumentsResponseDTO(BaseModel):
    """DTO para respuesta de múltiples documentos"""
    success: bool
    message: str
    data: Optional[DocumentListResponseDTO] = None