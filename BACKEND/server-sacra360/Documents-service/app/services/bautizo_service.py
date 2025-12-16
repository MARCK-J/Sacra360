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
        1. Busca si la persona ya existe (por datos básicos)
        2. Si existe, usa ese registro; si no existe, crea uno nuevo
        3. Verifica que la persona no tenga ya un bautizo registrado
        4. Crea registro en tabla sacramentos (tipo_id=1 para Bautizo)
        
        Args:
            dto: Datos del bautizo a registrar
            
        Returns:
            BautizoResponseDTO con IDs generados
            
        Raises:
            Exception si hay error en la transacción
        """
        try:
            # 1. Buscar si ya existe una persona con estos datos básicos
            # Criterio: nombres + apellidos + fecha_nacimiento
            persona_existente = self.db.query(PersonaModel).filter(
                PersonaModel.nombres == dto.nombres,
                PersonaModel.apellido_paterno == dto.apellido_paterno,
                PersonaModel.apellido_materno == dto.apellido_materno,
                PersonaModel.fecha_nacimiento == dto.fecha_nacimiento
            ).first()
            
            if persona_existente:
                # 2. Verificar si esta persona ya tiene un bautizo registrado (tipo_id=1)
                bautizo_existente = self.db.query(SacramentoModel).filter(
                    SacramentoModel.persona_id == persona_existente.id_persona,
                    SacramentoModel.tipo_id == 1  # Bautizo
                ).first()
                
                if bautizo_existente:
                    raise ValueError(
                        f"Esta persona ya tiene un bautizo registrado. "
                        f"Nombre: {dto.nombres} {dto.apellido_paterno} {dto.apellido_materno}, "
                        f"Fecha de nacimiento: {dto.fecha_nacimiento}, "
                        f"Sacramento ID: {bautizo_existente.id_sacramento}. "
                        f"No se puede registrar el mismo sacramento dos veces."
                    )
                
                # Persona existe pero no tiene bautizo: usar el registro existente
                persona = persona_existente
                print(f"✓ Usando persona existente (ID: {persona.id_persona})")
                
                # Actualizar fecha_bautismo si no estaba registrada
                if not persona.fecha_bautismo:
                    persona.fecha_bautismo = dto.fecha_bautismo
                    self.db.flush()
            else:
                # 3. Persona no existe: crear nuevo registro
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
                    print(f"✓ Persona creada (ID: {persona.id_persona})")
                except IntegrityError as e:
                    # Capturar violación de constraint único de PostgreSQL
                    if 'personas_datos_basicos_unique' in str(e):
                        raise ValueError(
                            f"Error de integridad: Esta persona ya está registrada. "
                            f"Nombre: {dto.nombres} {dto.apellido_paterno} {dto.apellido_materno}, "
                            f"Fecha de nacimiento: {dto.fecha_nacimiento}."
                        )
                    else:
                        raise
            
            # 4. Crear sacramento (tipo_id=1 para Bautizo)
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
            
            # 5. Commit de la transacción
            self.db.commit()
            
            return BautizoResponseDTO(
                persona_id=persona.id_persona,
                sacramento_id=sacramento.id_sacramento,
                mensaje="Bautizo registrado exitosamente"
            )
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al registrar bautizo: {str(e)}")
