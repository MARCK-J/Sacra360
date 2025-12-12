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
            
            # Obtener datos OCR para esta tupla (formato JSONB datos_ocr)
            tupla_ocr_raw = db.execute(
                text("""
                    SELECT id_ocr, datos_ocr, confianza, validado, sacramento_id, fuente_modelo
                    FROM ocr_resultado 
                    WHERE documento_id = :doc_id AND tupla_numero = :tupla_num
                    LIMIT 1
                """),
                {"doc_id": documento_id, "tupla_num": tupla_numero}
            ).fetchone()
            
            if tupla_ocr_raw:
                id_ocr = tupla_ocr_raw[0]
                datos_ocr = tupla_ocr_raw[1]  # JSONB dict
                confianza = float(tupla_ocr_raw[2])
                validado = tupla_ocr_raw[3]
                sacramento_id = tupla_ocr_raw[4]
                fuente_modelo = tupla_ocr_raw[5]
                
                # Convertir datos_ocr JSONB a formato campos_ocr para el frontend
                campos_response = []
                if isinstance(datos_ocr, dict):
                    # Iterar sobre col_0 a col_9, omitiendo col_4 (parroquia - no se valida)
                    for col_num in range(10):
                        # Saltar col_4 (parroquia)
                        if col_num == 4:
                            continue
                            
                        col_key = f"col_{col_num}"
                        if col_key in datos_ocr:
                            campos_response.append({
                                "id_ocr": id_ocr,
                                "campo": col_key,
                                "valor_extraido": datos_ocr[col_key],
                                "confianza": confianza,
                                "validado": validado,
                                "sacramento_id": sacramento_id
                            })
                
                tuplas_response.append({
                    "documento_id": documento_id,
                    "tupla_numero": tupla_numero,
                    "id_ocr": id_ocr,
                    "campos_ocr": campos_response,
                    "fuente_modelo": fuente_modelo,
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
        
        # Obtener el registro OCR actual
        ocr_actual = db.execute(
            text("""
                SELECT id_ocr, datos_ocr, fuente_modelo 
                FROM ocr_resultado 
                WHERE documento_id = :doc_id AND tupla_numero = :tupla_num
                LIMIT 1
            """),
            {"doc_id": documento_id, "tupla_num": tupla_numero}
        ).fetchone()
        
        if not ocr_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró tupla {tupla_numero} para documento {documento_id}"
            )
        
        id_ocr = ocr_actual[0]
        datos_ocr_originales = ocr_actual[1]  # JSONB dict
        fuente_modelo = ocr_actual[2]
        
        # Aplicar correcciones al JSONB datos_ocr
        datos_ocr_corregidos = dict(datos_ocr_originales) if isinstance(datos_ocr_originales, dict) else {}
        
        if correcciones:
            for correccion in correcciones:
                campo = correccion.get("campo")  # 'col_1', 'col_2', etc.
                valor_corregido = correccion.get("valor_corregido")
                
                if campo and campo in datos_ocr_corregidos:
                    # Guardar corrección en tabla correccion_documento
                    db.execute(
                        text("""
                            INSERT INTO correccion_documento 
                            (ocr_resultado_id, valor_original, valor_corregido, razon_correccion, usuario_id, fecha)
                            VALUES (:ocr_id, :valor_orig, :valor_corr, :razon, :usuario_id, NOW())
                        """),
                        {
                            "ocr_id": id_ocr,
                            "valor_orig": datos_ocr_corregidos[campo],
                            "valor_corr": valor_corregido,
                            "razon": correccion.get("comentario", "Corrección manual"),
                            "usuario_id": usuario_id
                        }
                    )
                    
                    # Actualizar el campo en datos_ocr
                    datos_ocr_corregidos[campo] = valor_corregido
            
            # Actualizar datos_ocr con las correcciones
            import json
            db.execute(
                text("""
                    UPDATE ocr_resultado 
                    SET datos_ocr = :datos_corregidos::jsonb, validado = true 
                    WHERE id_ocr = :ocr_id
                """),
                {
                    "datos_corregidos": json.dumps(datos_ocr_corregidos),
                    "ocr_id": id_ocr
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