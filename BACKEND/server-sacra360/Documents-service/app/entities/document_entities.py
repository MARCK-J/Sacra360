"""
Entidades de dominio para Documents Service
Modelos de datos para documentos sacramentales
"""

from pydantic import BaseModel, Field
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


# Entidades principales
class PersonEntity(BaseModel):
    """Entidad de persona"""
    id: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = None
    document_number: str = Field(..., min_length=5, max_length=20)
    document_type: str = Field(default="cedula")
    birth_date: datetime
    birth_place: str = Field(..., max_length=200)
    nationality: str = Field(default="Colombiana", max_length=100)
    gender: str = Field(..., regex="^(M|F|O)$")
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}"
    
    class Config:
        from_attributes = True


class ParishEntity(BaseModel):
    """Entidad de parroquia"""
    id: str
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., max_length=500)
    phone: Optional[str] = None
    email: Optional[str] = None
    diocese_id: str
    founded_date: Optional[datetime] = None
    patron_saint: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PriestEntity(BaseModel):
    """Entidad de sacerdote"""
    id: str
    user_id: str  # Referencia a AuthProfiles-service
    person_id: str  # Referencia a PersonEntity
    ordination_date: datetime
    parish_id: Optional[str] = None  # Parroquia actual
    diocese_id: str
    rank: str = Field(default="priest")  # priest, bishop, archbishop
    is_active: bool = Field(default=True)
    specializations: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentEntity(BaseModel):
    """Entidad principal de documento"""
    id: str
    document_type: DocumentType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: DocumentStatus = Field(default=DocumentStatus.DRAFT)
    
    # Referencias
    parish_id: str
    priest_id: str
    diocese_id: str
    
    # Metadatos sacramentales
    sacrament_type: Optional[SacramentType] = None
    sacrament_date: Optional[datetime] = None
    
    # Datos de registro
    book_number: Optional[str] = None
    page_number: Optional[str] = None
    record_number: Optional[str] = None
    
    # Participantes
    participants: List[str] = Field(default_factory=list)  # IDs de PersonEntity
    
    # Metadatos adicionales
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Archivos asociados
    file_paths: List[str] = Field(default_factory=list)
    
    # Auditoría
    created_at: datetime
    updated_at: datetime
    created_by: str
    last_modified_by: str
    
    # Validación y aprobación
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BaptismEntity(BaseModel):
    """Entidad específica para bautismo"""
    id: str
    document_id: str  # Referencia a DocumentEntity
    person_id: str  # Persona bautizada
    
    # Padres
    father_id: Optional[str] = None
    mother_id: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    
    # Padrinos
    godfather_id: Optional[str] = None
    godmother_id: Optional[str] = None
    godfather_name: Optional[str] = None
    godmother_name: Optional[str] = None
    
    # Datos específicos del bautismo
    baptism_date: datetime
    baptism_place: str
    
    # Registro
    book_number: str
    page_number: str
    record_number: str
    
    # Observaciones
    notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarriageEntity(BaseModel):
    """Entidad específica para matrimonio"""
    id: str
    document_id: str
    
    # Novios
    groom_id: str
    bride_id: str
    
    # Datos del matrimonio
    marriage_date: datetime
    marriage_place: str
    
    # Matrimonio civil
    civil_marriage_date: Optional[datetime] = None
    civil_marriage_place: Optional[str] = None
    civil_registration_number: Optional[str] = None
    
    # Testigos
    witness_1_id: Optional[str] = None
    witness_2_id: Optional[str] = None
    witness_1_name: Optional[str] = None
    witness_2_name: Optional[str] = None
    
    # Registro
    book_number: str
    page_number: str
    record_number: str
    
    # Observaciones
    notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeathEntity(BaseModel):
    """Entidad específica para defunción"""
    id: str
    document_id: str
    person_id: str
    
    # Datos de la defunción
    death_date: datetime
    death_place: str
    death_cause: Optional[str] = None
    death_time: Optional[str] = None
    
    # Estado civil al morir
    marital_status: str
    spouse_id: Optional[str] = None
    spouse_name: Optional[str] = None
    
    # Entierro
    burial_date: Optional[datetime] = None
    cemetery: Optional[str] = None
    burial_plot: Optional[str] = None
    
    # Registro
    book_number: str
    page_number: str
    record_number: str
    
    # Familiares informantes
    informant_name: Optional[str] = None
    informant_relationship: Optional[str] = None
    informant_document: Optional[str] = None
    
    # Observaciones
    notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConfirmationEntity(BaseModel):
    """Entidad específica para confirmación"""
    id: str
    document_id: str
    person_id: str
    
    # Datos de la confirmación
    confirmation_date: datetime
    confirmation_place: str
    
    # Padrino/Madrina
    sponsor_id: Optional[str] = None
    sponsor_name: Optional[str] = None
    
    # Obispo confirmante
    bishop_id: str
    bishop_name: str
    
    # Registro
    book_number: str
    page_number: str
    record_number: str
    
    # Observaciones
    notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentFileEntity(BaseModel):
    """Entidad para archivos asociados a documentos"""
    id: str
    document_id: str
    file_name: str
    file_path: str
    file_type: str  # pdf, jpg, png, etc.
    file_size: int
    mime_type: str
    is_original: bool = Field(default=False)
    is_processed: bool = Field(default=False)
    
    # Metadatos del archivo
    ocr_text: Optional[str] = None
    htr_text: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    
    uploaded_by: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class DocumentHistoryEntity(BaseModel):
    """Entidad para historial de cambios en documentos"""
    id: str
    document_id: str
    action: str  # created, updated, approved, rejected, etc.
    changes: Dict[str, Any]  # Campos modificados
    previous_values: Optional[Dict[str, Any]] = None
    user_id: str
    user_name: str
    timestamp: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# Entidades para búsquedas y estadísticas
class DocumentSearchResult(BaseModel):
    """Resultado de búsqueda de documentos"""
    documents: List[DocumentEntity]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class DocumentStatistics(BaseModel):
    """Estadísticas de documentos"""
    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    documents_by_parish: Dict[str, int]
    documents_by_month: Dict[str, int]
    recent_documents: List[DocumentEntity]
    generated_at: datetime