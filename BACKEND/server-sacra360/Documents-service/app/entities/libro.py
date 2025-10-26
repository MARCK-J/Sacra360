"""
Entidad Libro para el sistema Sacra360
Representa los libros de registros sacramentales
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Libro:
    """
    Entidad que representa un libro de registros sacramentales
    
    Attributes:
        id_libro: ID único del libro
        nombre: Nombre del libro
        fecha_inicio: Fecha de inicio del período que cubre el libro
        fecha_fin: Fecha de fin del período que cubre el libro
        observaciones: Observaciones opcionales del libro
    """
    id_libro: int
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    observaciones: Optional[str] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre del libro es obligatorio")
        
        if len(self.nombre) > 50:
            raise ValueError("El nombre no puede exceder 50 caracteres")
        
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")
        
        # Normalizar nombre
        self.nombre = self.nombre.strip()
        
        # Normalizar observaciones si existen
        if self.observaciones:
            self.observaciones = self.observaciones.strip()
            if len(self.observaciones) == 0:
                self.observaciones = None

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id_libro": self.id_libro,
            "nombre": self.nombre,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "observaciones": self.observaciones
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Libro":
        """Crea una instancia desde un diccionario"""
        return cls(
            id_libro=data["id_libro"],
            nombre=data["nombre"],
            fecha_inicio=data["fecha_inicio"],
            fecha_fin=data["fecha_fin"],
            observaciones=data.get("observaciones")
        )

    def __str__(self) -> str:
        return f"Libro(id={self.id_libro}, nombre='{self.nombre}', periodo={self.fecha_inicio} - {self.fecha_fin})"

    def __repr__(self) -> str:
        return self.__str__()