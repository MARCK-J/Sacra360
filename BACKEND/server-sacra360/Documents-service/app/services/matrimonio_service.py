"""
Servicio para gestionar registro de Matrimonios
"""
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.persona_model import PersonaModel
from app.models.sacramento_model import SacramentoModel
from app.models.matrimonio_model import MatrimonioModel
from app.dto.matrimonio_dto import MatrimonioCreateDTO, MatrimonioResponseDTO


class MatrimonioService:
    """Servicio para registrar matrimonios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_matrimonio(self, dto: MatrimonioCreateDTO) -> MatrimonioResponseDTO:
        """
        Registra un nuevo matrimonio:
        1. Crea 2 registros en tabla personas (esposo y esposa)
        2. Crea registro en tabla sacramentos (tipo_id=3 para Matrimonio, persona_id=esposo)
        3. Crea registro en tabla matrimonios con datos específicos
        
        Args:
            dto: Datos del matrimonio a registrar
            
        Returns:
            MatrimonioResponseDTO con IDs generados
            
        Raises:
            Exception si hay error en la transacción
        """
        try:
            # 1. Crear persona ESPOSO
            esposo = PersonaModel(
                nombres=dto.nombres_esposo,
                apellido_paterno=dto.apellido_paterno_esposo,
                apellido_materno=dto.apellido_materno_esposo,
                fecha_nacimiento=dto.fecha_nacimiento_esposo,
                fecha_bautismo=dto.fecha_bautismo_esposo,
                nombre_padre_nombre_madre=f"{dto.nombre_padre_esposo} - {dto.nombre_madre_esposo}",
                nombre_padrino_nombre_madrina=dto.nombre_padrino_nombre_madrina_esposo
            )
            self.db.add(esposo)
            self.db.flush()  # Para obtener el ID
            
            # 2. Crear persona ESPOSA
            esposa = PersonaModel(
                nombres=dto.nombres_esposa,
                apellido_paterno=dto.apellido_paterno_esposa,
                apellido_materno=dto.apellido_materno_esposa,
                fecha_nacimiento=dto.fecha_nacimiento_esposa,
                fecha_bautismo=dto.fecha_bautismo_esposa,
                nombre_padre_nombre_madre=f"{dto.nombre_padre_esposa} - {dto.nombre_madre_esposa}",
                nombre_padrino_nombre_madrina=dto.nombre_padrino_nombre_madrina_esposa
            )
            self.db.add(esposa)
            self.db.flush()
            
            # 3. Crear sacramento (tipo_id=3 para Matrimonio, persona_id apunta al esposo)
            sacramento = SacramentoModel(
                persona_id=esposo.id_persona,  # Por convención usamos el esposo
                tipo_id=3,  # Matrimonio
                usuario_id=dto.usuario_id,
                institucion_id=dto.institucion_id,
                libro_id=dto.libro_id,
                fecha_sacramento=dto.fecha_sacramento,
                fecha_registro=datetime.utcnow(),
                fecha_actualizacion=datetime.utcnow()
            )
            self.db.add(sacramento)
            self.db.flush()
            
            # 4. Crear registro en tabla matrimonios
            matrimonio = MatrimonioModel(
                sacramento_id=sacramento.id_sacramento,
                esposo_id=esposo.id_persona,
                esposa_id=esposa.id_persona,
                nombre_padre_esposo=dto.nombre_padre_esposo,
                nombre_madre_esposo=dto.nombre_madre_esposo,
                nombre_padre_esposa=dto.nombre_padre_esposa,
                nombre_madre_esposa=dto.nombre_madre_esposa,
                testigos=dto.testigos
            )
            self.db.add(matrimonio)
            self.db.flush()
            
            # 5. Commit de toda la transacción
            self.db.commit()
            
            return MatrimonioResponseDTO(
                esposo_id=esposo.id_persona,
                esposa_id=esposa.id_persona,
                sacramento_id=sacramento.id_sacramento,
                matrimonio_id=matrimonio.id_matrimonio,
                mensaje="Matrimonio registrado exitosamente"
            )
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al registrar matrimonio: {str(e)}")
