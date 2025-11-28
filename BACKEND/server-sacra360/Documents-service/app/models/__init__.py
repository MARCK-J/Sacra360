"""
Módulo de modelos SQLAlchemy
Importa todos los modelos para que estén disponibles
"""
from app.models.persona_model import PersonaModel
from app.models.libro_model import LibroModel
from app.models.tipo_sacramento_model import TipoSacramentoModel
from app.models.sacramento_model import SacramentoModel
from app.models.institucion_model import InstitucionModel
from app.models.usuario_model import UsuarioModel
from app.models.documento_model import DocumentoDigitalizadoModel
from app.models.validacion_model import ValidacionTupla
from app.models.correccion_model import CorreccionDocumento
from app.models.ocr_model import OCRResultado

__all__ = [
    "PersonaModel",
    "LibroModel",
    "TipoSacramentoModel",
    "SacramentoModel",
    "InstitucionModel",
    "UsuarioModel",
    "DocumentoDigitalizadoModel",
    "ValidacionTupla",
    "CorreccionDocumento",
    "OCRResultado"
]