from dataclasses import dataclass
from typing import Optional

@dataclass
class Resultado:
    id: str
    fecha_realizacion: Optional[str]          # "YYYY-MM-DD"
    puntuacion_total: Optional[int]
    interpretacion: Optional[str]
    comentario: Optional[str]
    id_test: Optional[str]                    # relación a test (o "test")
    id_paciente: Optional[str]                # relación a paciente (o "paciente")
    active: bool
    created: Optional[str] = None
    updated: Optional[str] = None
