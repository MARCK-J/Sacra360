"""
Endpoints para gestión de documentos digitalizados y OCR en el Sistema Sacra360
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional
from datetime import datetime

from ..schemas.sacra360_schemas import (
    DocumentoDigitalizadoCreate, DocumentoDigitalizadoResponse, DocumentoDigitalizadoUpdate,
    OCRResultadoResponse, OCRCorreccionCreate, OCRCorreccionResponse,
    MessageResponse
)
from .usuarios import get_current_user

# Configuración del router
router = APIRouter(prefix="/documentos", tags=["Documentos Digitalizados"])

# Simulación de base de datos en memoria
fake_documentos_db = {}
fake_ocr_resultados_db = {}
fake_ocr_correcciones_db = {}

documento_id_counter = 1
ocr_resultado_id_counter = 1
ocr_correccion_id_counter = 1


@router.post("/upload", response_model=DocumentoDigitalizadoResponse, status_code=status.HTTP_201_CREATED)
async def upload_documento(
    archivo: UploadFile = File(...),
    tipo_documento: str = Query(..., description="Tipo de documento (acta_bautizo, acta_matrimonio, etc.)"),
    descripcion: Optional[str] = Query(None, description="Descripción del documento"),
    current_user: dict = Depends(get_current_user)
):
    """
    Sube un nuevo documento digitalizado al sistema.
    
    Requiere permisos de secretario, sacerdote o administrador.
    """
    # Verificar permisos
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote", "secretario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para subir documentos"
        )
    
    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/tiff", "application/pdf"]
    if archivo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Solo se permiten: JPG, PNG, TIFF, PDF"
        )
    
    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if archivo.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo es demasiado grande. Máximo 10MB"
        )
    
    global documento_id_counter
    
    # Simular guardado del archivo
    filename = f"doc_{documento_id_counter}_{archivo.filename}"
    file_path = f"/uploads/{filename}"
    
    # En una implementación real, aquí se guardaría el archivo
    # with open(f"uploads/{filename}", "wb") as buffer:
    #     shutil.copyfileobj(archivo.file, buffer)
    
    # Crear registro del documento
    nuevo_documento = {
        "id_documento": documento_id_counter,
        "nombre_archivo": filename,
        "ruta_archivo": file_path,
        "tipo_documento": tipo_documento,
        "fecha_digitalizacion": datetime.now(),
        "tamano_archivo": archivo.size,
        "formato_archivo": archivo.content_type,
        "descripcion": descripcion,
        "estado_ocr": "pendiente",
        "id_usuario_carga": current_user.get("id_usuario")
    }
    
    fake_documentos_db[documento_id_counter] = nuevo_documento
    documento_id_counter += 1
    
    return DocumentoDigitalizadoResponse(**nuevo_documento)


@router.get("/", response_model=List[DocumentoDigitalizadoResponse])
async def get_documentos(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
    tipo_documento: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    estado_ocr: Optional[str] = Query(None, description="Filtrar por estado OCR"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de documentos digitalizados.
    """
    # Filtrar documentos
    filtered_documentos = list(fake_documentos_db.values())
    
    if tipo_documento:
        filtered_documentos = [
            d for d in filtered_documentos 
            if d["tipo_documento"] == tipo_documento
        ]
    
    if estado_ocr:
        filtered_documentos = [
            d for d in filtered_documentos 
            if d["estado_ocr"] == estado_ocr
        ]
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_documentos = filtered_documentos[start:end]
    
    return [DocumentoDigitalizadoResponse(**documento) for documento in paginated_documentos]


@router.get("/{documento_id}", response_model=DocumentoDigitalizadoResponse)
async def get_documento_by_id(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un documento por su ID.
    """
    documento = fake_documentos_db.get(documento_id)
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    return DocumentoDigitalizadoResponse(**documento)


@router.post("/{documento_id}/procesar-ocr", response_model=OCRResultadoResponse)
async def procesar_ocr(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Inicia el proceso de OCR para un documento.
    
    Requiere permisos de secretario, sacerdote o administrador.
    """
    # Verificar permisos
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote", "secretario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para procesar OCR"
        )
    
    documento = fake_documentos_db.get(documento_id)
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar que no haya sido procesado ya
    if documento["estado_ocr"] == "completado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El documento ya ha sido procesado"
        )
    
    global ocr_resultado_id_counter
    
    # Simular proceso de OCR
    # En una implementación real, aquí se llamaría al servicio de OCR
    texto_extraido = "Texto simulado extraído del documento mediante OCR..."
    
    # Crear resultado OCR
    nuevo_resultado_ocr = {
        "id_ocr_resultado": ocr_resultado_id_counter,
        "id_documento": documento_id,
        "texto_extraido": texto_extraido,
        "confianza_promedio": 85.5,
        "fecha_procesamiento": datetime.now(),
        "estado_revision": "pendiente"
    }
    
    fake_ocr_resultados_db[ocr_resultado_id_counter] = nuevo_resultado_ocr
    ocr_resultado_id_counter += 1
    
    # Actualizar estado del documento
    documento["estado_ocr"] = "completado"
    
    return OCRResultadoResponse(**nuevo_resultado_ocr)


@router.get("/{documento_id}/ocr", response_model=OCRResultadoResponse)
async def get_resultado_ocr(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene el resultado del OCR para un documento específico.
    """
    # Buscar resultado OCR para el documento
    resultado_ocr = None
    for resultado in fake_ocr_resultados_db.values():
        if resultado["id_documento"] == documento_id:
            resultado_ocr = resultado
            break
    
    if not resultado_ocr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró resultado de OCR para este documento"
        )
    
    return OCRResultadoResponse(**resultado_ocr)


@router.post("/{documento_id}/ocr/corregir", response_model=OCRCorreccionResponse)
async def crear_correccion_ocr(
    documento_id: int,
    correccion_data: OCRCorreccionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crea una corrección para el resultado de OCR.
    
    Permite a los usuarios corregir errores en el texto extraído.
    """
    # Verificar que existe el resultado OCR
    resultado_ocr = None
    for resultado in fake_ocr_resultados_db.values():
        if resultado["id_documento"] == documento_id:
            resultado_ocr = resultado
            break
    
    if not resultado_ocr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró resultado de OCR para este documento"
        )
    
    global ocr_correccion_id_counter
    
    # Crear corrección
    nueva_correccion = {
        "id_correccion": ocr_correccion_id_counter,
        "id_ocr_resultado": resultado_ocr["id_ocr_resultado"],
        "texto_original": correccion_data.texto_original,
        "texto_corregido": correccion_data.texto_corregido,
        "posicion_inicio": correccion_data.posicion_inicio,
        "posicion_fin": correccion_data.posicion_fin,
        "fecha_correccion": datetime.now(),
        "id_usuario_correccion": current_user.get("id_usuario"),
        "observaciones": correccion_data.observaciones
    }
    
    fake_ocr_correcciones_db[ocr_correccion_id_counter] = nueva_correccion
    ocr_correccion_id_counter += 1
    
    return OCRCorreccionResponse(**nueva_correccion)


@router.get("/{documento_id}/ocr/correcciones", response_model=List[OCRCorreccionResponse])
async def get_correcciones_ocr(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todas las correcciones realizadas al OCR de un documento.
    """
    # Buscar resultado OCR para el documento
    resultado_ocr = None
    for resultado in fake_ocr_resultados_db.values():
        if resultado["id_documento"] == documento_id:
            resultado_ocr = resultado
            break
    
    if not resultado_ocr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró resultado de OCR para este documento"
        )
    
    # Buscar correcciones para el resultado OCR
    correcciones = [
        correccion for correccion in fake_ocr_correcciones_db.values()
        if correccion["id_ocr_resultado"] == resultado_ocr["id_ocr_resultado"]
    ]
    
    return [OCRCorreccionResponse(**correccion) for correccion in correcciones]


@router.put("/{documento_id}", response_model=DocumentoDigitalizadoResponse)
async def update_documento(
    documento_id: int,
    documento_update: DocumentoDigitalizadoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza la información de un documento.
    
    Requiere permisos de secretario, sacerdote o administrador.
    """
    # Verificar permisos
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote", "secretario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar documentos"
        )
    
    documento = fake_documentos_db.get(documento_id)
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Obtener datos a actualizar
    update_data = documento_update.model_dump(exclude_unset=True)
    
    # Actualizar campos
    for field, value in update_data.items():
        documento[field] = value
    
    return DocumentoDigitalizadoResponse(**documento)


@router.delete("/{documento_id}", response_model=MessageResponse)
async def delete_documento(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un documento del sistema.
    
    Solo administradores pueden eliminar documentos.
    También elimina los resultados OCR y correcciones asociadas.
    """
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar documentos"
        )
    
    if documento_id not in fake_documentos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Eliminar resultados OCR asociados
    ocr_resultados_to_delete = []
    for ocr_id, resultado in fake_ocr_resultados_db.items():
        if resultado["id_documento"] == documento_id:
            ocr_resultados_to_delete.append(ocr_id)
    
    # Eliminar correcciones asociadas a los resultados OCR
    for ocr_id in ocr_resultados_to_delete:
        correcciones_to_delete = []
        for corr_id, correccion in fake_ocr_correcciones_db.items():
            if correccion["id_ocr_resultado"] == ocr_id:
                correcciones_to_delete.append(corr_id)
        
        for corr_id in correcciones_to_delete:
            del fake_ocr_correcciones_db[corr_id]
        
        del fake_ocr_resultados_db[ocr_id]
    
    # Eliminar el documento
    del fake_documentos_db[documento_id]
    
    # En una implementación real, también eliminar el archivo físico
    
    return MessageResponse(
        message="Documento y datos asociados eliminados exitosamente",
        success=True
    )