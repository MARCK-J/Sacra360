"""
Controlador para manejar la validación de tuplas OCR
Permite a los usuarios validar y corregir resultados de OCR antes del registro final
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.services.validacion_service import ValidacionService
from app.dto.validacion_dto import (
    TuplaValidacionResponse,
    ValidacionRequest,
    ValidacionCompleteRequest,
    ValidacionStatusResponse
)

router = APIRouter()
validacion_service = ValidacionService()

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
    Obtiene las tuplas OCR pendientes de validación para un documento en formato JSON.
    
    Args:
        documento_id: ID del documento digitalizado
        
    Returns:
        Lista de tuplas con datos_ocr en formato JSON
    """
    try:
        from sqlalchemy import text
        import json
        
        query = text("""
            SELECT 
                id_ocr,
                tupla_numero,
                datos_ocr,
                confianza,
                estado_validacion
            FROM ocr_resultado
            WHERE documento_id = :doc_id
            AND estado_validacion = 'pendiente'
            ORDER BY tupla_numero
        """)
        
        result = db.execute(query, {"doc_id": documento_id})
        tuplas = []
        
        for row in result:
            # Parsear el JSON de datos_ocr
            datos_json = row[2] if isinstance(row[2], dict) else json.loads(row[2])
            
            tuplas.append({
                "id_ocr": row[0],
                "tupla_numero": row[1],
                "datos_ocr": datos_json,
                "campos_ocr": [
                    {
                        "id_ocr": row[0],
                        "campo": campo,
                        "valor_extraido": valor,
                        "confianza": float(row[3]),
                        "validado": False
                    }
                    for campo, valor in datos_json.items()
                ],
                "confianza": float(row[3]),
                "estado_validacion": row[4],
                "total_tuplas_documento": None  # Se llenará después
            })
        
        # Calcular total de tuplas del documento
        if tuplas:
            query_total = text("""
                SELECT COUNT(*) FROM ocr_resultado WHERE documento_id = :doc_id
            """)
            total = db.execute(query_total, {"doc_id": documento_id}).scalar()
            for tupla in tuplas:
                tupla["total_tuplas_documento"] = total
        
        return tuplas
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tuplas pendientes: {str(e)}"
        )

@router.get(
    "/tupla/{documento_id}/{tupla_numero}",
    response_model=TuplaValidacionResponse,
    summary="Obtener tupla específica",
    description="Obtiene los datos OCR de una tupla específica para validación"
)
async def obtener_tupla_especifica(
    documento_id: int,
    tupla_numero: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los datos OCR de una tupla específica.
    
    Args:
        documento_id: ID del documento digitalizado
        tupla_numero: Número de la tupla a obtener
        
    Returns:
        Datos de la tupla con información OCR
    """
    try:
        tupla = await validacion_service.obtener_tupla_especifica(documento_id, tupla_numero, db)
        return tupla
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tupla: {str(e)}"
        )

@router.post(
    "/validar-tupla",
    summary="Validar una tupla OCR y registrar en personas/sacramentos",
    description="Valida una tupla OCR y la registra inmediatamente en las tablas personas y sacramentos"
)
async def validar_tupla(
    validacion_data: ValidacionRequest,
    db: Session = Depends(get_db)
):
    """
    Valida una tupla OCR, registra en personas y sacramentos.
    
    Args:
        validacion_data: Datos de validación con campos corregidos e institucion_id
        
    Returns:
        Estado de la validación, IDs creados y siguiente tupla
    """
    try:
        # Validar que se haya proporcionado la institución
        if not validacion_data.institucion_id:
            raise ValueError("Debe seleccionar una institución/parroquia")
        
        # Llamar al servicio que registra en personas y sacramentos
        resultado = await validacion_service.validar_tupla_json(
            documento_id=validacion_data.documento_id,
            tupla_numero=validacion_data.tupla_numero,
            campos_corregidos=validacion_data.datos_validados,
            usuario_id=validacion_data.usuario_validador_id,
            institucion_id=validacion_data.institucion_id,
            db=db
        )
        
        # Verificar si todas las tuplas están validadas
        query_total = text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado_validacion = 'validado' THEN 1 ELSE 0 END) as validadas
            FROM ocr_resultado
            WHERE documento_id = :doc_id
        """)
        
        stats = db.execute(query_total, {"doc_id": validacion_data.documento_id}).fetchone()
        total_tuplas = stats[0]
        tuplas_validadas = stats[1]
        
        # Si todas las tuplas están validadas, actualizar estado del documento
        completado = (total_tuplas == tuplas_validadas)
        
        if completado:
            update_doc = text("""
                UPDATE documento_digitalizado
                SET estado_procesamiento = 'validado',
                    fecha_validacion = NOW()
                WHERE id_documento = :doc_id
            """)
            db.execute(update_doc, {"doc_id": validacion_data.documento_id})
            db.commit()
        
        return {
            "success": resultado["success"],
            "mensaje": resultado["message"],
            "persona_id": resultado["persona_id"],
            "sacramento_id": resultado["sacramento_id"],
            "siguiente_tupla": resultado["siguiente_tupla"],
            "completado": completado,
            "total_tuplas": total_tuplas,
            "tuplas_validadas": tuplas_validadas,
            "tuplas_pendientes": total_tuplas - tuplas_validadas
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar tupla: {str(e)}"
        )

@router.post(
    "/completar-validacion/{documento_id}",
    response_model=ValidacionStatusResponse,
    summary="Completar validación de documento",
    description="Finaliza el proceso de validación y registra todos los sacramentos validados"
)
async def completar_validacion_documento(
    documento_id: int,
    completion_data: ValidacionCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Completa la validación de un documento y registra los sacramentos.
    
    Args:
        documento_id: ID del documento digitalizado
        completion_data: Datos finales de completación
        
    Returns:
        Estado final de la validación
    """
    try:
        resultado = await validacion_service.completar_validacion_documento(
            documento_id, completion_data, db
        )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al completar validación: {str(e)}"
        )

@router.get(
    "/estado-validacion/{documento_id}",
    response_model=Dict[str, Any],
    summary="Obtener estado de validación",
    description="Obtiene el estado actual del proceso de validación de un documento"
)
async def obtener_estado_validacion(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado actual de validación de un documento.
    
    Args:
        documento_id: ID del documento digitalizado
        
    Returns:
        Información del estado de validación
    """
    try:
        estado = await validacion_service.obtener_estado_validacion(documento_id, db)
        return estado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado: {str(e)}"
        )

@router.delete(
    "/cancelar-validacion/{documento_id}",
    summary="Cancelar proceso de validación",
    description="Cancela el proceso de validación y marca las tuplas como pendientes"
)
async def cancelar_validacion(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancela el proceso de validación de un documento.
    
    Args:
        documento_id: ID del documento digitalizado
        
    Returns:
        Confirmación de cancelación
    """
    try:
        await validacion_service.cancelar_validacion(documento_id, db)
        return {"message": "Validación cancelada exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar validación: {str(e)}"
        )

@router.get("/tuplas-pendientes-json/{documento_id}")
async def obtener_tuplas_pendientes_json(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las tuplas pendientes en formato JSON (nueva estructura).
    
    Retorna los datos OCR completos como JSON por cada tupla,
    en lugar de campos individuales.
    """
    try:
        tuplas = await validacion_service.obtener_tuplas_pendientes_json(documento_id, db)
        return {
            "documento_id": documento_id,
            "total_tuplas": len(tuplas),
            "tuplas": tuplas
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tuplas: {str(e)}"
        )

@router.post("/validar-tupla-json")
async def validar_tupla_json(
    documento_id: int,
    tupla_numero: int,
    campos_corregidos: Dict[str, Any],
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Valida una tupla con estructura JSON y registra en personas y sacramentos.
    
    Este endpoint:
    1. Obtiene los datos OCR de la tupla (almacenados como JSON)
    2. Aplica las correcciones del usuario
    3. Crea un registro en la tabla personas
    4. Crea un registro en la tabla sacramentos
    5. Marca la tupla como validada
    
    Args:
        documento_id: ID del documento
        tupla_numero: Número de la tupla (1-10)
        campos_corregidos: Diccionario con los campos validados/corregidos
        usuario_id: ID del usuario que valida
        
    Returns:
        Resultado de la validación con IDs creados
    """
    try:
        resultado = await validacion_service.validar_tupla_json(
            documento_id=documento_id,
            tupla_numero=tupla_numero,
            campos_corregidos=campos_corregidos,
            usuario_id=usuario_id,
            db=db
        )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar tupla: {str(e)}"
        )

@router.get(
    "/instituciones",
    summary="Obtener lista de instituciones/parroquias",
    description="Obtiene todas las instituciones y parroquias registradas en el sistema"
)
async def obtener_instituciones(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todas las instituciones/parroquias disponibles.
    
    Returns:
        Lista de instituciones con id, nombre, dirección, teléfono y email
    """
    try:
        query = text("""
            SELECT 
                id_institucion,
                nombre,
                direccion,
                telefono,
                email
            FROM InstitucionesParroquias
            ORDER BY nombre
        """)
        
        result = db.execute(query)
        instituciones = []
        
        for row in result:
            instituciones.append({
                "id_institucion": row[0],
                "nombre": row[1],
                "direccion": row[2],
                "telefono": row[3],
                "email": row[4]
            })
        
        return {
            "total": len(instituciones),
            "instituciones": instituciones
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener instituciones: {str(e)}"
        )