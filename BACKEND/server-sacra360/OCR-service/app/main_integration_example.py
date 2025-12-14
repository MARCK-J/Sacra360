"""
Ejemplo de integración completa del OCR GPU en tu aplicación Sacra360.
Este archivo muestra cómo integrar el nuevo procesador GPU en el main.py existente.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# Importar los nuevos routers de OCR GPU
from app.ocr_endpoints_gpu import router as ocr_gpu_router

# Tu configuración existente...
app = FastAPI(
    title="Sacra360 OCR Service",
    description="Servicio de OCR con aceleración GPU para procesamiento de documentos sacramentales",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INTEGRACIÓN DE OCR GPU - NUEVO
# ============================================================================

# Incluir los nuevos endpoints de OCR GPU
app.include_router(ocr_gpu_router)

# Endpoint de salud que incluye verificación de GPU
@app.get("/health")
async def health_check():
    """Health check con información de GPU."""
    try:
        from app.ocr_gpu_processor import TableOCRProcessor
        processor = TableOCRProcessor(use_gpu=True)
        gpu_info = processor.get_gpu_info()
        
        return {
            "status": "healthy",
            "service": "ocr-service",
            "version": "2.0.0",
            "gpu": {
                "available": gpu_info["cuda_available"],
                "device": gpu_info["device_name"],
                "count": gpu_info["device_count"]
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "ocr-service",
            "version": "2.0.0",
            "gpu": {
                "available": False,
                "error": str(e)
            }
        }


# Endpoint raíz con información
@app.get("/")
async def root():
    """Información del servicio."""
    return {
        "service": "Sacra360 OCR Service",
        "version": "2.0.0",
        "gpu_enabled": True,
        "endpoints": {
            "health": "/health",
            "gpu_status": "/ocr-gpu/gpu-status",
            "process_table": "/ocr-gpu/process-table",
            "batch_process": "/ocr-gpu/batch-process"
        },
        "documentation": "/docs"
    }


# ============================================================================
# EJEMPLO DE USO PROGRAMÁTICO
# ============================================================================

async def ejemplo_procesamiento_documento(pdf_path: str):
    """
    Ejemplo de cómo usar el procesador GPU directamente en tu código.
    """
    from app.ocr_gpu_processor import TableOCRProcessor
    
    # Crear procesador
    processor = TableOCRProcessor(
        use_gpu=True,
        languages=['en', 'es'],
        dpi=150
    )
    
    # Procesar documento
    df = processor.process_pdf_table(
        pdf_path=pdf_path,
        page_number=0,
        num_cols=10,
        pattern=['L', 'N', 'N', 'N', 'L', 'N', 'N', 'N', 'L', 'L']
    )
    
    # Hacer algo con los resultados
    print(f"Extraídas {len(df)} filas")
    
    # Guardar en base de datos, enviar por API, etc.
    return df


# ============================================================================
# EJEMPLO DE PROCESAMIENTO EN BACKGROUND
# ============================================================================

from fastapi import BackgroundTasks

@app.post("/ocr-gpu/process-async")
async def process_document_async(
    background_tasks: BackgroundTasks,
    file_path: str
):
    """
    Procesa un documento en background.
    Útil para documentos grandes que toman más tiempo.
    """
    
    def process_in_background(path: str):
        """Tarea de procesamiento en background."""
        try:
            from app.ocr_gpu_processor import process_table_pdf
            
            # Procesar
            df = process_table_pdf(path, use_gpu=True)
            
            # Guardar resultado
            output_path = path.replace('.pdf', '_processed.csv')
            df.to_csv(output_path, index=False)
            
            # Aquí podrías actualizar una base de datos, enviar notificación, etc.
            logging.info(f"Documento procesado: {path} -> {output_path}")
            
        except Exception as e:
            logging.error(f"Error procesando en background: {e}")
    
    # Agregar tarea al background
    background_tasks.add_task(process_in_background, file_path)
    
    return {
        "status": "processing",
        "message": "Documento en cola de procesamiento",
        "file": file_path
    }


# ============================================================================
# EJEMPLO DE INTEGRACIÓN CON MINIO (STORAGE)
# ============================================================================

from minio import Minio
import tempfile
import os

# Configurar cliente Minio (usando variables de entorno)
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
    secure=False
)

@app.post("/ocr-gpu/process-from-storage")
async def process_document_from_storage(
    bucket_name: str,
    object_name: str,
    use_gpu: bool = True
):
    """
    Procesa un documento directamente desde Minio storage.
    """
    try:
        # Descargar archivo de Minio a archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
            minio_client.fget_object(bucket_name, object_name, tmp_path)
        
        # Procesar con GPU
        from app.ocr_gpu_processor import process_table_pdf
        df = process_table_pdf(tmp_path, use_gpu=use_gpu)
        
        # Guardar resultado de vuelta a Minio
        result_csv = tmp_path.replace('.pdf', '_result.csv')
        df.to_csv(result_csv, index=False)
        
        result_object_name = object_name.replace('.pdf', '_result.csv')
        minio_client.fput_object(bucket_name, result_object_name, result_csv)
        
        # Limpiar archivos temporales
        os.remove(tmp_path)
        os.remove(result_csv)
        
        return {
            "status": "success",
            "source": f"{bucket_name}/{object_name}",
            "result": f"{bucket_name}/{result_object_name}",
            "rows": len(df),
            "columns": len(df.columns),
            "gpu_used": use_gpu
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EJEMPLO DE CACHÉ CON REDIS
# ============================================================================

import hashlib
import json
from typing import Optional
import redis

# Cliente Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

def get_cache_key(file_path: str, page: int) -> str:
    """Genera clave de caché basada en hash del archivo."""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return f"ocr:table:{file_hash}:page:{page}"


async def process_with_cache(file_path: str, page: int = 0) -> dict:
    """
    Procesa documento con caché en Redis.
    Si ya fue procesado antes, retorna resultado cacheado.
    """
    cache_key = get_cache_key(file_path, page)
    
    # Verificar caché
    cached_result = redis_client.get(cache_key)
    if cached_result:
        logging.info(f"Resultado obtenido de caché: {cache_key}")
        return json.loads(cached_result)
    
    # No está en caché, procesar con GPU
    from app.ocr_gpu_processor import process_table_pdf
    df = process_table_pdf(file_path, page_number=page, use_gpu=True)
    
    # Preparar resultado
    result = {
        "rows": len(df),
        "columns": len(df.columns),
        "data": df.to_dict(orient='records')
    }
    
    # Guardar en caché (expira en 24 horas)
    redis_client.setex(
        cache_key,
        86400,  # 24 horas
        json.dumps(result)
    )
    
    return result


@app.post("/ocr-gpu/process-cached")
async def process_document_cached(file_path: str, page: int = 0):
    """Endpoint que usa caché de Redis."""
    try:
        result = await process_with_cache(file_path, page)
        return {
            "status": "success",
            "cached": False,  # Agregar lógica para detectar si vino de caché
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP EVENT - WARMUP GPU
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio: precalentar GPU con una inferencia dummy.
    La primera inferencia suele ser más lenta, así que la hacemos al inicio.
    """
    logging.info("Iniciando servicio OCR con GPU...")
    
    try:
        from app.ocr_gpu_processor import TableOCRProcessor
        
        # Crear procesador
        processor = TableOCRProcessor(use_gpu=True)
        gpu_info = processor.get_gpu_info()
        
        if gpu_info["cuda_available"]:
            logging.info(f"GPU detectada: {gpu_info['device_name']}")
            logging.info("GPU lista para procesamiento")
        else:
            logging.warning("GPU no disponible, usando CPU")
            
    except Exception as e:
        logging.error(f"Error inicializando GPU: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False  # Desactivar reload en producción
    )
