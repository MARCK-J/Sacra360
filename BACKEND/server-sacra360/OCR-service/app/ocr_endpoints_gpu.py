"""
Ejemplo de endpoint para OCR con GPU en el servicio OCR de Sacra360.
Este archivo muestra cómo integrar el TableOCRProcessor en tu API.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from typing import Optional
import logging

from .ocr_gpu_processor import TableOCRProcessor, process_table_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr-gpu", tags=["OCR GPU"])


@router.get("/gpu-status")
async def get_gpu_status():
    """
    Verifica el estado de la GPU y disponibilidad de CUDA.
    
    Returns:
        Información sobre GPU disponible
    """
    try:
        processor = TableOCRProcessor(use_gpu=True)
        gpu_info = processor.get_gpu_info()
        
        return {
            "status": "success",
            "gpu_enabled": gpu_info["cuda_available"],
            "cuda_version": gpu_info["cuda_version"],
            "device_count": gpu_info["device_count"],
            "device_name": gpu_info["device_name"],
            "message": "GPU disponible y lista para usar" if gpu_info["cuda_available"] 
                      else "GPU no disponible, usando CPU"
        }
    except Exception as e:
        logger.error(f"Error verificando GPU: {e}")
        return {
            "status": "error",
            "gpu_enabled": False,
            "message": str(e)
        }


@router.post("/process-table")
async def process_table_document(
    file: UploadFile = File(...),
    page_number: int = 0,
    num_cols: int = 10,
    use_gpu: bool = True,
    output_format: str = "json"
):
    """
    Procesa un documento PDF y extrae una tabla usando OCR con GPU.
    
    Args:
        file: Archivo PDF a procesar
        page_number: Número de página (0-indexed)
        num_cols: Número esperado de columnas
        use_gpu: Activar aceleración GPU (recomendado)
        output_format: Formato de salida ("json" o "csv")
    
    Returns:
        Tabla extraída en formato especificado
    """
    # Validar tipo de archivo
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_path = tmp_file.name
        content = await file.read()
        tmp_file.write(content)
    
    try:
        logger.info(f"Procesando {file.filename} con GPU: {use_gpu}")
        
        # Procesar tabla con OCR GPU
        df = process_table_pdf(
            pdf_path=tmp_path,
            page_number=page_number,
            use_gpu=use_gpu
        )
        
        # Formatear respuesta
        if output_format == "csv":
            csv_data = df.to_csv(index=False)
            return JSONResponse(content={
                "status": "success",
                "filename": file.filename,
                "rows": len(df),
                "columns": len(df.columns),
                "data_csv": csv_data,
                "gpu_used": use_gpu
            })
        else:
            # Formato JSON
            data = df.to_dict(orient='records')
            return JSONResponse(content={
                "status": "success",
                "filename": file.filename,
                "rows": len(df),
                "columns": len(df.columns),
                "data": data,
                "column_names": list(df.columns),
                "gpu_used": use_gpu
            })
    
    except Exception as e:
        logger.error(f"Error procesando documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/batch-process")
async def batch_process_tables(
    files: list[UploadFile] = File(...),
    use_gpu: bool = True
):
    """
    Procesa múltiples documentos PDF en lote usando GPU.
    
    Args:
        files: Lista de archivos PDF
        use_gpu: Activar aceleración GPU
    
    Returns:
        Resultados de todos los documentos procesados
    """
    results = []
    processor = TableOCRProcessor(use_gpu=use_gpu)
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "Formato no válido. Solo PDF."
            })
            continue
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
            content = await file.read()
            tmp_file.write(content)
        
        try:
            df = processor.process_pdf_table(tmp_path)
            results.append({
                "filename": file.filename,
                "status": "success",
                "rows": len(df),
                "columns": len(df.columns),
                "data": df.to_dict(orient='records')
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    return {
        "status": "success",
        "total_files": len(files),
        "processed": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results,
        "gpu_used": use_gpu
    }


# Para integrar estos endpoints en tu aplicación principal:
# En app/main.py:
# from app.ocr_endpoints_gpu import router as ocr_gpu_router
# app.include_router(ocr_gpu_router)
