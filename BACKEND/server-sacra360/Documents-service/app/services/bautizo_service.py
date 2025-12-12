"""
Servicio para gestionar registro de Bautizos
"""
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.persona_model import PersonaModel
from app.models.sacramento_model import SacramentoModel
from app.dto.bautizo_dto import BautizoCreateDTO, BautizoResponseDTO


class BautizoService:
    """Servicio para registrar bautizos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_bautizo(self, dto: BautizoCreateDTO) -> BautizoResponseDTO:
        """
        Registra un nuevo bautizo:
        1. Crea registro en tabla personas
        2. Crea registro en tabla sacramentos (tipo_id=1 para Bautizo)
        
        Args:
            dto: Datos del bautizo a registrar
            
        Returns:
            BautizoResponseDTO con IDs generados
            
        Raises:
            Exception si hay error en la transacción
        """
        try:
            # VALIDACIÓN: Verificar si ya existe una persona con estos datos
            # Criterio: nombres + apellidos + fecha_nacimiento + fecha_bautismo
            persona_existente = self.db.query(PersonaModel).filter(
                PersonaModel.nombres == dto.nombres,
                PersonaModel.apellido_paterno == dto.apellido_paterno,
                PersonaModel.apellido_materno == dto.apellido_materno,
                PersonaModel.fecha_nacimiento == dto.fecha_nacimiento,
                PersonaModel.fecha_bautismo == dto.fecha_bautismo
            ).first()
            
            if persona_existente:
                raise ValueError(
                    f"Esta persona ya está registrada en el sistema. "
                    f"Nombre: {dto.nombres} {dto.apellido_paterno} {dto.apellido_materno}, "
                    f"Fecha de nacimiento: {dto.fecha_nacimiento}, "
                    f"Fecha de bautizo: {dto.fecha_bautismo}. "
                    f"Por favor, verifique los datos o use el registro existente."
                )
            
            # 1. Crear persona
            try:
                persona = PersonaModel(
                    nombres=dto.nombres,
                    apellido_paterno=dto.apellido_paterno,
                    apellido_materno=dto.apellido_materno,
                    fecha_nacimiento=dto.fecha_nacimiento,
                    fecha_bautismo=dto.fecha_bautismo,
                    nombre_padre_nombre_madre=dto.nombre_padre_nombre_madre,
                    nombre_padrino_nombre_madrina=dto.nombre_padrino_nombre_madrina
                )
                self.db.add(persona)
                self.db.flush()  # Para obtener el ID de persona
            except IntegrityError as e:
                # Capturar violación de constraint único de PostgreSQL
                if 'personas_datos_basicos_unique' in str(e):
                    raise ValueError(
                        f"Esta persona ya está registrada en el sistema. "
                        f"Nombre: {dto.nombres} {dto.apellido_paterno} {dto.apellido_materno}, "
                        f"Fecha de nacimiento: {dto.fecha_nacimiento}, "
                        f"Fecha de bautizo: {dto.fecha_bautismo}. "
                        f"Por favor, verifique los datos o use el registro existente."
                    )
                else:
                    raise
            
            # 2. Crear sacramento (tipo_id=1 para Bautizo)
            sacramento = SacramentoModel(
                persona_id=persona.id_persona,
                tipo_id=1,  # Bautizo
                usuario_id=dto.usuario_id,
                institucion_id=dto.institucion_id,
                libro_id=dto.libro_id,
                fecha_sacramento=dto.fecha_sacramento,
                fecha_registro=datetime.utcnow(),
                fecha_actualizacion=datetime.utcnow()
            )
            self.db.add(sacramento)
            self.db.flush()
            
            # 3. Commit de la transacción
            self.db.commit()
            
            return BautizoResponseDTO(
                persona_id=persona.id_persona,
                sacramento_id=sacramento.id_sacramento,
                mensaje="Bautizo registrado exitosamente"
            )
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al registrar bautizo: {str(e)}")
