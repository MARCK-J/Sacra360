"""
Entidad TipoSacramento para el sistema Sacra360
Representa los tipos de sacramentos disponibles
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TipoSacramento:
    """
    Entidad que representa un tipo de sacramento
    
    Attributes:
        id_tipo: ID único del tipo de sacramento
        nombre: Nombre del tipo de sacramento (ej: Bautismo, Confirmación, Matrimonio)
        descripcion: Descripción opcional del tipo de sacramento
    """
    id_tipo: int
    nombre: str
    descripcion: Optional[str] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre del tipo de sacramento es obligatorio")
        
        if len(self.nombre) > 50:
            raise ValueError("El nombre no puede exceder 50 caracteres")
        
        # Normalizar nombre (capitalizar primera letra)
        self.nombre = self.nombre.strip().title()
        
        # Normalizar descripción si existe
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
            if len(self.descripcion) == 0:
                self.descripcion = None

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id_tipo": self.id_tipo,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TipoSacramento":
        """Crea una instancia desde un diccionario"""
        return cls(
            id_tipo=data["id_tipo"],
            nombre=data["nombre"],
            descripcion=data.get("descripcion")
        )

    def __str__(self) -> str:
        return f"TipoSacramento(id={self.id_tipo}, nombre='{self.nombre}')"

    def __repr__(self) -> str:
        return self.__str__()