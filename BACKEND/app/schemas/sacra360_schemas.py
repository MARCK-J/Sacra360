"""
Schemas Pydantic para el Sistema Sacra360
Sistema de gestión de sacramentos parroquiales con digitalización de documentos
"""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ================================
# ENUMS DEL SISTEMA SACRA360
# ================================

class TipoSacramento(str, Enum):
    """Tipos de sacramentos disponibles"""
    BAUTIZO = "bautizo"
    CONFIRMACION = "confirmacion"
    MATRIMONIO = "matrimonio"
    COMUNION = "comunion"
    PENITENCIA = "penitencia"
    UNCION = "uncion"
    ORDEN = "orden"


class AccionAuditoria(str, Enum):
    """Acciones registradas en auditoría"""
    CREAR = "crear"
    ACTUALIZAR = "actualizar"
    ELIMINAR = "eliminar"
    VISUALIZAR = "visualizar"
    LOGIN = "login"
    LOGOUT = "logout"


class EstadoUsuario(str, Enum):
    """Estados de usuario"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"


class TipoRol(str, Enum):
    """Roles del sistema"""
    ADMIN = "admin"
    SACERDOTE = "sacerdote"
    SECRETARIO = "secretario"
    CONSULTOR = "consultor"


# ================================
# SCHEMA BASE
# ================================

class BaseSchema(BaseModel):
    """Schema base con configuración común para Sacra360"""
    
    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "use_enum_values": True
    }


# ================================
# SCHEMAS DE ROLES
# ================================

class RolBase(BaseSchema):
    """Schema base para roles"""
    rol: str = Field(..., min_length=3, max_length=50, description="Nombre del rol")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del rol")


class RolCreate(RolBase):
    """Schema para crear rol"""
    pass


class RolUpdate(BaseSchema):
    """Schema para actualizar rol"""
    rol: Optional[str] = Field(None, min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)


class RolResponse(RolBase):
    """Schema para respuesta de rol"""
    id_rol: int = Field(..., description="ID único del rol")


# ================================
# SCHEMAS DE USUARIOS
# ================================

class UsuarioBase(BaseSchema):
    """Schema base para usuarios del sistema"""
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario")
    apellido_paterno: Optional[str] = Field(None, max_length=50, description="Apellido paterno")
    apellido_materno: Optional[str] = Field(None, max_length=50, description="Apellido materno")
    email: str = Field(..., max_length=100, description="Email único del usuario")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento")
    activo: bool = Field(True, description="Usuario activo")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Email debe tener formato válido')
        return v.lower()


class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña del usuario")
    confirm_password: str = Field(..., description="Confirmación de contraseña")
    id_rol: int = Field(..., description="ID del rol asignado")
    
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


class UsuarioUpdate(BaseSchema):
    """Schema para actualizar usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido_paterno: Optional[str] = Field(None, max_length=50)
    apellido_materno: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    fecha_nacimiento: Optional[date] = None
    activo: Optional[bool] = None
    id_rol: Optional[int] = None


class UsuarioResponse(UsuarioBase):
    """Schema para respuesta de usuario"""
    id_usuario: int = Field(..., description="ID único del usuario")
    rol: Optional[RolResponse] = Field(None, description="Información del rol")
    
    @property
    def nombre_completo(self) -> str:
        """Nombre completo del usuario"""
        nombres = [self.nombre]
        if self.apellido_paterno:
            nombres.append(self.apellido_paterno)
        if self.apellido_materno:
            nombres.append(self.apellido_materno)
        return " ".join(nombres)


# ================================
# SCHEMAS DE INSTITUCIONES PARROQUIALES
# ================================

class InstitucionBase(BaseSchema):
    """Schema base para instituciones parroquiales"""
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre de la institución")
    direccion: Optional[str] = Field(None, max_length=150, description="Dirección")
    telefono: Optional[str] = Field(None, max_length=15, description="Teléfono")
    email: Optional[str] = Field(None, max_length=100, description="Email institucional")
    
    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v and not v.replace('-', '').replace(' ', '').replace('+', '').isdigit():
            raise ValueError('Teléfono debe contener solo números, espacios, guiones y +')
        return v


class InstitucionCreate(InstitucionBase):
    """Schema para crear institución"""
    pass


class InstitucionUpdate(BaseSchema):
    """Schema para actualizar institución"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    direccion: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=15)
    email: Optional[str] = Field(None, max_length=100)


class InstitucionResponse(InstitucionBase):
    """Schema para respuesta de institución"""
    id_institucion: int = Field(..., description="ID único de la institución")


# ================================
# SCHEMAS DE TIPOS DE SACRAMENTOS
# ================================

class TipoSacramentoBase(BaseSchema):
    """Schema base para tipos de sacramentos"""
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del tipo de sacramento")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del sacramento")


class TipoSacramentoCreate(TipoSacramentoBase):
    """Schema para crear tipo de sacramento"""
    pass


class TipoSacramentoUpdate(BaseSchema):
    """Schema para actualizar tipo de sacramento"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)


class TipoSacramentoResponse(TipoSacramentoBase):
    """Schema para respuesta de tipo de sacramento"""
    id_tipo: int = Field(..., description="ID único del tipo de sacramento")


# ================================
# SCHEMAS DE PERSONAS
# ================================

class PersonaBase(BaseSchema):
    """Schema base para personas"""
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres de la persona")
    apellido_paterno: Optional[str] = Field(None, max_length=50, description="Apellido paterno")
    apellido_materno: Optional[str] = Field(None, max_length=50, description="Apellido materno")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento")
    lugar_nacimiento: Optional[str] = Field(None, max_length=100, description="Lugar de nacimiento")
    nombre_padre: Optional[str] = Field(None, max_length=100, description="Nombre del padre")
    nombre_madre: Optional[str] = Field(None, max_length=100, description="Nombre de la madre")


class PersonaCreate(PersonaBase):
    """Schema para crear persona"""
    pass


class PersonaUpdate(BaseSchema):
    """Schema para actualizar persona"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido_paterno: Optional[str] = Field(None, max_length=50)
    apellido_materno: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = Field(None, max_length=100)
    nombre_padre: Optional[str] = Field(None, max_length=100)
    nombre_madre: Optional[str] = Field(None, max_length=100)


class PersonaResponse(PersonaBase):
    """Schema para respuesta de persona"""
    id_persona: int = Field(..., description="ID único de la persona")
    
    @property
    def nombre_completo(self) -> str:
        """Nombre completo de la persona"""
        nombres = [self.nombres]
        if self.apellido_paterno:
            nombres.append(self.apellido_paterno)
        if self.apellido_materno:
            nombres.append(self.apellido_materno)
        return " ".join(nombres)


# ================================
# SCHEMAS DE LIBROS
# ================================

class LibroBase(BaseSchema):
    """Schema base para libros sacramentales"""
    nombre: Optional[str] = Field(None, max_length=50, description="Nombre del libro")
    tipo: Optional[str] = Field(None, max_length=50, description="Tipo de libro")
    fecha_inicio: Optional[date] = Field(None, description="Fecha de inicio del libro")
    fecha_fin: Optional[date] = Field(None, description="Fecha de fin del libro")
    observaciones: Optional[str] = Field(None, description="Observaciones del libro")
    
    @field_validator('fecha_fin')
    @classmethod
    def validate_fechas(cls, v, info):
        if v and hasattr(info, 'data') and info.data.get('fecha_inicio') and v < info.data['fecha_inicio']:
            raise ValueError('La fecha de fin no puede ser anterior a la fecha de inicio')
        return v


class LibroCreate(LibroBase):
    """Schema para crear libro"""
    pass


class LibroUpdate(BaseSchema):
    """Schema para actualizar libro"""
    nombre: Optional[str] = Field(None, max_length=50)
    tipo: Optional[str] = Field(None, max_length=50)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = None


class LibroResponse(LibroBase):
    """Schema para respuesta de libro"""
    id_libro: int = Field(..., description="ID único del libro")


# ================================
# SCHEMAS DE SACRAMENTOS
# ================================

class SacramentoBase(BaseSchema):
    """Schema base para sacramentos"""
    fecha_sacramento: date = Field(..., description="Fecha del sacramento")
    
    @field_validator('fecha_sacramento')
    @classmethod
    def validate_fecha_sacramento(cls, v):
        if v > date.today():
            raise ValueError('La fecha del sacramento no puede ser futura')
        return v


class SacramentoCreate(SacramentoBase):
    """Schema para crear sacramento"""
    id_persona: int = Field(..., description="ID de la persona")
    id_tipo: int = Field(..., description="ID del tipo de sacramento")
    id_usuario: int = Field(..., description="ID del usuario que registra")
    id_institucion: int = Field(..., description="ID de la institución")
    id_libro: Optional[int] = Field(None, description="ID del libro sacramental")


class SacramentoUpdate(BaseSchema):
    """Schema para actualizar sacramento"""
    fecha_sacramento: Optional[date] = None
    id_persona: Optional[int] = None
    id_tipo: Optional[int] = None
    id_usuario: Optional[int] = None
    id_institucion: Optional[int] = None
    id_libro: Optional[int] = None


class SacramentoResponse(SacramentoBase):
    """Schema para respuesta de sacramento"""
    id_sacramento: int = Field(..., description="ID único del sacramento")
    fecha_registro: datetime = Field(..., description="Fecha de registro")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    # Relaciones
    persona: Optional[PersonaResponse] = None
    tipo_sacramento: Optional[TipoSacramentoResponse] = None
    usuario: Optional[UsuarioResponse] = None
    institucion: Optional[InstitucionResponse] = None
    libro: Optional[LibroResponse] = None


# ================================
# SCHEMAS DE DETALLES DE SACRAMENTOS
# ================================

class DetallesBautizoBase(BaseSchema):
    """Schema base para detalles de bautizo"""
    padrino: Optional[str] = Field(None, max_length=100, description="Nombre del padrino")
    ministro: Optional[str] = Field(None, max_length=100, description="Nombre del ministro")
    foja: Optional[str] = Field(None, max_length=10, description="Número de foja")
    numero: Optional[str] = Field(None, max_length=10, description="Número de registro")
    fecha_bautizo: Optional[date] = Field(None, description="Fecha específica del bautizo")


class DetallesBautizoCreate(DetallesBautizoBase):
    """Schema para crear detalles de bautizo"""
    id_sacramento: int = Field(..., description="ID del sacramento")


class DetallesBautizoUpdate(BaseSchema):
    """Schema para actualizar detalles de bautizo"""
    padrino: Optional[str] = Field(None, max_length=100)
    ministro: Optional[str] = Field(None, max_length=100)
    foja: Optional[str] = Field(None, max_length=10)
    numero: Optional[str] = Field(None, max_length=10)
    fecha_bautizo: Optional[date] = None


class DetallesBautizoResponse(DetallesBautizoBase):
    """Schema para respuesta de detalles de bautizo"""
    id_bautizo: int = Field(..., description="ID único del detalle de bautizo")
    id_sacramento: int = Field(..., description="ID del sacramento")


class DetallesConfirmacionBase(BaseSchema):
    """Schema base para detalles de confirmación"""
    padrino: Optional[str] = Field(None, max_length=100, description="Nombre del padrino")
    ministro: Optional[str] = Field(None, max_length=100, description="Nombre del ministro")
    foja: Optional[str] = Field(None, max_length=10, description="Número de foja")
    numero: Optional[str] = Field(None, max_length=10, description="Número de registro")
    fecha_confirmacion: Optional[date] = Field(None, description="Fecha específica de la confirmación")


class DetallesConfirmacionCreate(DetallesConfirmacionBase):
    """Schema para crear detalles de confirmación"""
    id_sacramento: int = Field(..., description="ID del sacramento")


class DetallesConfirmacionResponse(DetallesConfirmacionBase):
    """Schema para respuesta de detalles de confirmación"""
    id_confirmacion: int = Field(..., description="ID único del detalle de confirmación")
    id_sacramento: int = Field(..., description="ID del sacramento")


class DetallesMatrimonioBase(BaseSchema):
    """Schema base para detalles de matrimonio"""
    nombre_esposo: Optional[str] = Field(None, max_length=100, description="Nombre del esposo")
    nombre_esposa: Optional[str] = Field(None, max_length=100, description="Nombre de la esposa")
    apellido_paterno_esposo: Optional[str] = Field(None, max_length=50, description="Apellido paterno del esposo")
    apellido_materno_esposo: Optional[str] = Field(None, max_length=50, description="Apellido materno del esposo")
    apellido_paterno_esposa: Optional[str] = Field(None, max_length=50, description="Apellido paterno de la esposa")
    apellido_materno_esposa: Optional[str] = Field(None, max_length=50, description="Apellido materno de la esposa")
    nombre_padre_esposo: Optional[str] = Field(None, max_length=100, description="Nombre del padre del esposo")
    nombre_madre_esposo: Optional[str] = Field(None, max_length=100, description="Nombre de la madre del esposo")
    nombre_padre_esposa: Optional[str] = Field(None, max_length=100, description="Nombre del padre de la esposa")
    nombre_madre_esposa: Optional[str] = Field(None, max_length=100, description="Nombre de la madre de la esposa")
    padrino: Optional[str] = Field(None, max_length=100, description="Nombre del padrino")
    ministro: Optional[str] = Field(None, max_length=100, description="Nombre del ministro")
    foja: Optional[str] = Field(None, max_length=10, description="Número de foja")
    numero: Optional[str] = Field(None, max_length=10, description="Número de registro")
    reg_civil: Optional[str] = Field(None, max_length=100, description="Registro civil")
    fecha_matrimonio: Optional[date] = Field(None, description="Fecha específica del matrimonio")
    lugar_matrimonio: Optional[str] = Field(None, max_length=100, description="Lugar del matrimonio")


class DetallesMatrimonioCreate(DetallesMatrimonioBase):
    """Schema para crear detalles de matrimonio"""
    id_sacramento: int = Field(..., description="ID del sacramento")


class DetallesMatrimonioResponse(DetallesMatrimonioBase):
    """Schema para respuesta de detalles de matrimonio"""
    id_matrimonio: int = Field(..., description="ID único del detalle de matrimonio")
    id_sacramento: int = Field(..., description="ID del sacramento")


# ================================
# SCHEMAS DE DOCUMENTOS DIGITALIZADOS
# ================================

class DocumentoDigitalizadoBase(BaseSchema):
    """Schema base para documentos digitalizados"""
    tipo_sacramento: str = Field(..., max_length=50, description="Tipo de sacramento del documento")
    imagen_url: str = Field(..., description="URL de la imagen del documento")
    ocr_texto: Optional[str] = Field(None, description="Texto extraído por OCR")
    modelo_fuente: Optional[str] = Field(None, max_length=100, description="Modelo usado para OCR")
    confianza: Optional[Decimal] = Field(None, ge=0, le=1, description="Nivel de confianza del OCR")


class DocumentoDigitalizadoCreate(DocumentoDigitalizadoBase):
    """Schema para crear documento digitalizado"""
    libro_id: Optional[int] = Field(None, description="ID del libro asociado")


class DocumentoDigitalizadoUpdate(BaseSchema):
    """Schema para actualizar documento digitalizado"""
    tipo_sacramento: Optional[str] = Field(None, max_length=50)
    libro_id: Optional[int] = None
    imagen_url: Optional[str] = None
    ocr_texto: Optional[str] = None
    modelo_fuente: Optional[str] = Field(None, max_length=100)
    confianza: Optional[Decimal] = Field(None, ge=0, le=1)


class DocumentoDigitalizadoResponse(DocumentoDigitalizadoBase):
    """Schema para respuesta de documento digitalizado"""
    id_documento: int = Field(..., description="ID único del documento")
    fecha_procesamiento: datetime = Field(..., description="Fecha de procesamiento")
    libro: Optional[LibroResponse] = None


# ================================
# SCHEMAS DE RESULTADOS OCR
# ================================

class OCRResultadoBase(BaseSchema):
    """Schema base para resultados OCR"""
    campo: str = Field(..., max_length=50, description="Campo extraído")
    valor_extraido: str = Field(..., description="Valor extraído del campo")
    confianza: Optional[Decimal] = Field(None, ge=0, le=1, description="Nivel de confianza")
    fuente_modelo: Optional[str] = Field(None, max_length=100, description="Modelo que extrajo el valor")
    validado: Optional[bool] = Field(None, description="Si el valor ha sido validado")


class OCRResultadoCreate(OCRResultadoBase):
    """Schema para crear resultado OCR"""
    documento_id: int = Field(..., description="ID del documento")


class OCRResultadoUpdate(BaseSchema):
    """Schema para actualizar resultado OCR"""
    campo: Optional[str] = Field(None, max_length=50)
    valor_extraido: Optional[str] = None
    confianza: Optional[Decimal] = Field(None, ge=0, le=1)
    fuente_modelo: Optional[str] = Field(None, max_length=100)
    validado: Optional[bool] = None


class OCRResultadoResponse(OCRResultadoBase):
    """Schema para respuesta de resultado OCR"""
    id_ocr: int = Field(..., description="ID único del resultado OCR")
    documento_id: int = Field(..., description="ID del documento")


# ================================
# SCHEMAS DE CORRECCIONES
# ================================

class CorreccionDocumentoBase(BaseSchema):
    """Schema base para correcciones de documentos"""
    valor_original: str = Field(..., description="Valor original extraído")
    valor_corregido: str = Field(..., description="Valor corregido")


class CorreccionDocumentoCreate(CorreccionDocumentoBase):
    """Schema para crear corrección"""
    ocr_resultado_id: int = Field(..., description="ID del resultado OCR")
    id_usuario: int = Field(..., description="ID del usuario que hace la corrección")


class CorreccionDocumentoResponse(CorreccionDocumentoBase):
    """Schema para respuesta de corrección"""
    id_correccion: int = Field(..., description="ID único de la corrección")
    fecha: datetime = Field(..., description="Fecha de la corrección")
    usuario: Optional[UsuarioResponse] = None


# ================================
# SCHEMAS DE AUDITORÍA
# ================================

class AuditoriaBase(BaseSchema):
    """Schema base para auditoría"""
    accion: AccionAuditoria = Field(..., description="Acción realizada")
    entidad: str = Field(..., description="Entidad afectada")
    entidad_id: Optional[int] = Field(None, description="ID de la entidad afectada")


class AuditoriaCreate(AuditoriaBase):
    """Schema para crear registro de auditoría"""
    usuario_id: Optional[int] = Field(None, description="ID del usuario")


class AuditoriaResponse(AuditoriaBase):
    """Schema para respuesta de auditoría"""
    id_auditoria: int = Field(..., description="ID único del registro de auditoría")
    fecha: datetime = Field(..., description="Fecha del registro")
    usuario: Optional[UsuarioResponse] = None


# ================================
# SCHEMAS DE AUTENTICACIÓN
# ================================

class LoginRequest(BaseSchema):
    """Schema para solicitud de login"""
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña")


class Token(BaseSchema):
    """Schema para token de acceso"""
    access_token: str = Field(..., description="Token de acceso JWT")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user_info: UsuarioResponse = Field(..., description="Información del usuario")


# ================================
# SCHEMAS DE RESPUESTA GENERAL
# ================================

class MessageResponse(BaseSchema):
    """Schema para respuestas con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(True, description="Indica si la operación fue exitosa")


class ErrorResponse(BaseSchema):
    """Schema para respuestas de error"""
    error: str = Field(..., description="Descripción del error")
    detail: Optional[str] = Field(None, description="Detalle adicional del error")
    code: Optional[str] = Field(None, description="Código de error")


class PaginatedResponse(BaseSchema):
    """Schema base para respuestas paginadas"""
    total: int = Field(..., description="Total de elementos")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Elementos por página")
    total_pages: int = Field(..., description="Total de páginas")


class PaginationParams(BaseSchema):
    """Schema para parámetros de paginación"""
    page: int = Field(1, ge=1, description="Número de página")
    limit: int = Field(10, ge=1, le=100, description="Límite de elementos por página")
    sort_by: Optional[str] = Field("id", description="Campo por el cual ordenar")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Orden ascendente o descendente")


# ================================
# SCHEMAS ESPECÍFICOS PARA CONSULTAS
# ================================

class BusquedaPersona(BaseSchema):
    """Schema para búsqueda de personas"""
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    fecha_nacimiento_desde: Optional[date] = None
    fecha_nacimiento_hasta: Optional[date] = None


class BusquedaSacramento(BaseSchema):
    """Schema para búsqueda de sacramentos"""
    tipo_sacramento: Optional[TipoSacramento] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    institucion_id: Optional[int] = None
    persona_id: Optional[int] = None


class EstadisticasSacramentos(BaseSchema):
    """Schema para estadísticas de sacramentos"""
    total_sacramentos: int
    sacramentos_por_tipo: dict
    sacramentos_por_mes: dict
    instituciones_mas_activas: List[dict]


# ================================
# SCHEMAS DE BÚSQUEDA ESPECÍFICOS POR SACRAMENTO
# ================================

class BautizoBusqueda(BaseSchema):
    """Schema para búsqueda específica de bautizos"""
    nombre_padrino: Optional[str] = Field(None, description="Nombre del padrino")
    nombre_madrina: Optional[str] = Field(None, description="Nombre de la madrina")
    fecha_desde: Optional[date] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[date] = Field(None, description="Fecha hasta")


class ConfirmacionBusqueda(BaseSchema):
    """Schema para búsqueda específica de confirmaciones"""
    nombre_padrino: Optional[str] = Field(None, description="Nombre del padrino")
    fecha_desde: Optional[date] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[date] = Field(None, description="Fecha hasta")


class MatrimonioBusqueda(BaseSchema):
    """Schema para búsqueda específica de matrimonios"""
    nombre_testigo1: Optional[str] = Field(None, description="Nombre del primer testigo")
    nombre_testigo2: Optional[str] = Field(None, description="Nombre del segundo testigo")
    fecha_desde: Optional[date] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[date] = Field(None, description="Fecha hasta")


# ================================
# SCHEMAS PARA OCR CORRECCIONES
# ================================

class OCRCorreccionCreate(BaseSchema):
    """Schema para crear corrección de OCR"""
    texto_original: str = Field(..., description="Texto original del OCR")
    texto_corregido: str = Field(..., description="Texto corregido")
    posicion_inicio: Optional[int] = Field(None, description="Posición de inicio en el texto")
    posicion_fin: Optional[int] = Field(None, description="Posición de fin en el texto")
    observaciones: Optional[str] = Field(None, description="Observaciones sobre la corrección")


class OCRCorreccionResponse(BaseSchema):
    """Schema para respuesta de corrección de OCR"""
    id_correccion: int = Field(..., description="ID de la corrección")
    id_ocr_resultado: int = Field(..., description="ID del resultado OCR")
    texto_original: str = Field(..., description="Texto original del OCR")
    texto_corregido: str = Field(..., description="Texto corregido")
    posicion_inicio: Optional[int] = Field(None, description="Posición de inicio en el texto")
    posicion_fin: Optional[int] = Field(None, description="Posición de fin en el texto")
    fecha_correccion: datetime = Field(..., description="Fecha de la corrección")
    id_usuario_correccion: int = Field(..., description="ID del usuario que hizo la corrección")
    observaciones: Optional[str] = Field(None, description="Observaciones sobre la corrección")