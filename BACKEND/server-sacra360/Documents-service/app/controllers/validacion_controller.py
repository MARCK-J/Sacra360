"""
Controlador para manejar la validación de tuplas OCR
Permite a los usuarios validar y corregir resultados de OCR antes del registro final
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    response_model=List[TuplaValidacionResponse],
    summary="Obtener tuplas pendientes de validación",
    description="Obtiene todas las tuplas OCR que están pendientes de validación para un documento específico"
)
async def obtener_tuplas_pendientes(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las tuplas OCR pendientes de validación para un documento.
    
    Args:
        documento_id: ID del documento digitalizado
        
    Returns:
        Lista de tuplas agrupadas con sus datos OCR
    """
    try:
        tuplas = await validacion_service.obtener_tuplas_pendientes(documento_id, db)
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
    response_model=ValidacionStatusResponse,
    summary="Validar una tupla OCR",
    description="Valida una tupla OCR con posibles correcciones del usuario"
)
async def validar_tupla(
    validacion_data: ValidacionRequest,
    db: Session = Depends(get_db)
):
    """
    Valida una tupla OCR, aplicando correcciones si es necesario.
    
    Args:
        validacion_data: Datos de validación incluyendo correcciones
        
    Returns:
        Estado de la validación y siguiente tupla disponible
    """
    try:
        resultado = await validacion_service.validar_tupla(validacion_data, db)
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