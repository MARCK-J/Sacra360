"""
Controlador simplificado para validación de tuplas OCR
Versión temporal sin relaciones complejas de SQLAlchemy
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get(
    "/tuplas-pendientes/{documento_id}",
    summary="Obtener tuplas pendientes de validación",
    description="Obtiene todas las tuplas OCR que están pendientes de validación para un documento específico"
)
async def obtener_tuplas_pendientes(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las tuplas OCR pendientes de validación para un documento.
    """
    try:
        # Verificar que el documento existe
        documento_exists = db.execute(
            text("SELECT COUNT(*) FROM documento_digitalizado WHERE id_documento = :doc_id"),
            {"doc_id": documento_id}
        ).scalar()
        
        if documento_exists == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento con ID {documento_id} no encontrado"
            )
        
        # Obtener números de tuplas pendientes
        tuplas_pendientes = db.execute(
            text("""
                SELECT DISTINCT tupla_numero 
                FROM validacion_tuplas 
                WHERE documento_id = :doc_id AND estado = 'pendiente'
                ORDER BY tupla_numero
            """),
            {"doc_id": documento_id}
        ).fetchall()
        
        if not tuplas_pendientes:
            return []
        
        # Obtener total de tuplas del documento
        total_tuplas = db.execute(
            text("""
                SELECT COALESCE(MAX(tupla_numero), 0) 
                FROM ocr_resultado 
                WHERE documento_id = :doc_id
            """),
            {"doc_id": documento_id}
        ).scalar() or 0
        
        tuplas_response = []
        
        for tupla_row in tuplas_pendientes:
            tupla_numero = tupla_row[0]
            
            # Obtener campos OCR para esta tupla
            campos_ocr_raw = db.execute(
                text("""
                    SELECT id_ocr, campo, valor_extraido, confianza, validado, sacramento_id
                    FROM ocr_resultado 
                    WHERE documento_id = :doc_id AND tupla_numero = :tupla_num
                    ORDER BY campo
                """),
                {"doc_id": documento_id, "tupla_num": tupla_numero}
            ).fetchall()
            
            if campos_ocr_raw:
                campos_response = []
                for campo_row in campos_ocr_raw:
                    campos_response.append({
                        "id_ocr": campo_row[0],
                        "campo": campo_row[1],
                        "valor_extraido": campo_row[2],
                        "confianza": float(campo_row[3]),
                        "validado": campo_row[4],
                        "sacramento_id": campo_row[5]
                    })
                
                tuplas_response.append({
                    "documento_id": documento_id,
                    "tupla_numero": tupla_numero,
                    "campos_ocr": campos_response,
                    "estado_validacion": "pendiente",
                    "total_tuplas_documento": total_tuplas
                })
        
        return tuplas_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tuplas pendientes: {str(e)}"
        )

@router.post(
    "/validar-tupla",
    summary="Validar una tupla OCR",
    description="Valida una tupla OCR con posibles correcciones del usuario"
)
async def validar_tupla(
    validacion_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Valida una tupla OCR, aplicando correcciones si es necesario.
    """
    try:
        documento_id = validacion_data["documento_id"]
        tupla_numero = validacion_data["tupla_numero"]
        usuario_id = validacion_data.get("usuario_validador_id", 1)
        correcciones = validacion_data.get("correcciones", [])
        observaciones = validacion_data.get("observaciones", "")
        accion = validacion_data["accion"]  # 'aprobar', 'corregir', 'rechazar'
        
        # Aplicar correcciones si las hay
        if correcciones:
            for correccion in correcciones:
                # Actualizar el valor en OCR resultado
                db.execute(
                    text("""
                        UPDATE ocr_resultado 
                        SET valor_extraido = :nuevo_valor, validado = true 
                        WHERE id_ocr = :ocr_id
                    """),
                    {
                        "nuevo_valor": correccion["valor_corregido"],
                        "ocr_id": correccion["id_ocr"]
                    }
                )
                
                # Crear registro de corrección (tabla simplificada)
                db.execute(
                    text("""
                        INSERT INTO correccion_documento 
                        (ocr_resultado_id, valor_original, valor_corregido, razon_correccion, usuario_corrector_id, fecha_correccion)
                        VALUES (:ocr_id, :valor_orig, :valor_corr, :razon, :usuario_id, NOW())
                    """),
                    {
                        "ocr_id": correccion["id_ocr"],
                        "valor_orig": correccion["valor_original"],
                        "valor_corr": correccion["valor_corregido"],
                        "razon": correccion.get("comentario", "Corrección manual"),
                        "usuario_id": usuario_id
                    }
                )
        
        # Actualizar estado de validación según la acción
        nuevo_estado = "validado" if accion in ["aprobar", "corregir"] else "rechazado"
        
        db.execute(
            text("""
                UPDATE validacion_tuplas 
                SET estado = :estado, usuario_validador_id = :usuario_id, 
                    fecha_validacion = NOW(), observaciones = :obs
                WHERE documento_id = :doc_id AND tupla_numero = :tupla_num
            """),
            {
                "estado": nuevo_estado,
                "usuario_id": usuario_id,
                "obs": observaciones,
                "doc_id": documento_id,
                "tupla_num": tupla_numero
            }
        )
        
        # Marcar campos OCR como validados/rechazados
        if accion != "rechazar":
            db.execute(
                text("""
                    UPDATE ocr_resultado 
                    SET validado = true, estado_validacion = :estado_val
                    WHERE documento_id = :doc_id AND tupla_numero = :tupla_num
                """),
                {
                    "estado_val": "corregido" if correcciones else "validado",
                    "doc_id": documento_id,
                    "tupla_num": tupla_numero
                }
            )
        
        db.commit()
        
        # Obtener estadísticas actuales
        total_tuplas = db.execute(
            text("SELECT COUNT(*) FROM validacion_tuplas WHERE documento_id = :doc_id"),
            {"doc_id": documento_id}
        ).scalar()
        
        tuplas_validadas = db.execute(
            text("SELECT COUNT(*) FROM validacion_tuplas WHERE documento_id = :doc_id AND estado = 'validado'"),
            {"doc_id": documento_id}
        ).scalar()
        
        tuplas_pendientes = total_tuplas - tuplas_validadas
        
        # Obtener siguiente tupla pendiente
        siguiente_tupla_row = db.execute(
            text("""
                SELECT tupla_numero FROM validacion_tuplas 
                WHERE documento_id = :doc_id AND estado = 'pendiente' AND tupla_numero > :tupla_actual
                ORDER BY tupla_numero LIMIT 1
            """),
            {"doc_id": documento_id, "tupla_actual": tupla_numero}
        ).fetchone()
        
        siguiente_tupla_num = siguiente_tupla_row[0] if siguiente_tupla_row else None
        completado = tuplas_pendientes == 0
        
        return {
            "documento_id": documento_id,
            "tupla_actual": tupla_numero,
            "tupla_validada": True,
            "siguiente_tupla": siguiente_tupla_num,
            "tuplas_pendientes": tuplas_pendientes,
            "tuplas_validadas": tuplas_validadas,
            "total_tuplas": total_tuplas,
            "completado": completado,
            "mensaje": "Tupla validada exitosamente" + (f". Siguiente: {siguiente_tupla_num}" if siguiente_tupla_num else ". Validación completa.")
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar tupla: {str(e)}"
        )

@router.get(
    "/estado-validacion/{documento_id}",
    summary="Obtener estado de validación",
    description="Obtiene el estado actual del proceso de validación de un documento"
)
async def obtener_estado_validacion(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado actual de validación de un documento.
    """
    try:
        # Verificar que el documento existe
        documento_info = db.execute(
            text("SELECT nombre_archivo, tipo_sacramento FROM documento_digitalizado WHERE id_documento = :doc_id"),
            {"doc_id": documento_id}
        ).fetchone()
        
        if not documento_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {documento_id} no encontrado"
            )
        
        # Estadísticas de validación
        total_tuplas = db.execute(
            text("SELECT COUNT(*) FROM validacion_tuplas WHERE documento_id = :doc_id"),
            {"doc_id": documento_id}
        ).scalar()
        
        tuplas_validadas = db.execute(
            text("SELECT COUNT(*) FROM validacion_tuplas WHERE documento_id = :doc_id AND estado = 'validado'"),
            {"doc_id": documento_id}
        ).scalar()
        
        tuplas_pendientes = db.execute(
            text("SELECT COUNT(*) FROM validacion_tuplas WHERE documento_id = :doc_id AND estado = 'pendiente'"),
            {"doc_id": documento_id}
        ).scalar()
        
        tuplas_rechazadas = db.execute(
            text("SELECT COUNT(*) FROM validacion_tuplas WHERE documento_id = :doc_id AND estado = 'rechazado'"),
            {"doc_id": documento_id}
        ).scalar()
        
        progreso = (tuplas_validadas / total_tuplas * 100) if total_tuplas > 0 else 0
        
        estado_general = "completado" if tuplas_pendientes == 0 and tuplas_validadas == total_tuplas else ("en_progreso" if tuplas_validadas > 0 else "pendiente")
        
        return {
            "documento_id": documento_id,
            "nombre_archivo": documento_info[0] if documento_info[0] else f"documento_{documento_id}",
            "tipo_sacramento": documento_info[1] if documento_info[1] else "desconocido",
            "total_tuplas": total_tuplas,
            "tuplas_validadas": tuplas_validadas,
            "tuplas_pendientes": tuplas_pendientes,
            "tuplas_rechazadas": tuplas_rechazadas,
            "progreso_porcentaje": round(progreso, 2),
            "estado_general": estado_general
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado de validación: {str(e)}"
        )