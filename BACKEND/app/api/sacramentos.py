"""
Endpoints para gestión de sacramentos en el Sistema Sacra360
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date

from ..schemas.sacra360_schemas import (
    SacramentoCreate, SacramentoResponse, SacramentoUpdate,
    BautizoBusqueda, ConfirmacionBusqueda, MatrimonioBusqueda,
    MessageResponse
)
from .usuarios import get_current_user

# Configuración del router
router = APIRouter(prefix="/sacramentos", tags=["Sacramentos"])

# Simulación de base de datos en memoria
fake_sacramentos_db = {}
sacramento_id_counter = 1

# Simulación de personas (para validar que existan)
fake_personas_db = {1: {"id_persona": 1, "nombres": "Juan", "apellido_paterno": "Pérez"}}


@router.post("/", response_model=SacramentoResponse, status_code=status.HTTP_201_CREATED)
async def create_sacramento(
    sacramento_data: SacramentoCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Registra un nuevo sacramento.
    
    Requiere permisos de sacerdote, secretario o administrador.
    """
    # Verificar permisos
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote", "secretario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para registrar sacramentos"
        )
    
    global sacramento_id_counter
    
    # Verificar que la persona existe
    if sacramento_data.id_persona not in fake_personas_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La persona especificada no existe"
        )
    
    # Validaciones específicas por tipo de sacramento
    if sacramento_data.tipo_sacramento == "bautizo":
        if not sacramento_data.detalles_bautizo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los detalles del bautizo son requeridos"
            )
    
    elif sacramento_data.tipo_sacramento == "confirmacion":
        if not sacramento_data.detalles_confirmacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los detalles de la confirmación son requeridos"
            )
    
    elif sacramento_data.tipo_sacramento == "matrimonio":
        if not sacramento_data.detalles_matrimonio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los detalles del matrimonio son requeridos"
            )
        # Verificar que el cónyuge existe
        if sacramento_data.detalles_matrimonio.id_conyuge not in fake_personas_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cónyuge especificado no existe"
            )
    
    # Crear el sacramento
    nuevo_sacramento = {
        "id_sacramento": sacramento_id_counter,
        "id_persona": sacramento_data.id_persona,
        "tipo_sacramento": sacramento_data.tipo_sacramento,
        "fecha_sacramento": sacramento_data.fecha_sacramento,
        "parroquia": sacramento_data.parroquia,
        "celebrante": sacramento_data.celebrante,
        "libro": sacramento_data.libro,
        "folio": sacramento_data.folio,
        "numero": sacramento_data.numero,
        "observaciones": sacramento_data.observaciones,
        "detalles_bautizo": sacramento_data.detalles_bautizo.model_dump() if sacramento_data.detalles_bautizo else None,
        "detalles_confirmacion": sacramento_data.detalles_confirmacion.model_dump() if sacramento_data.detalles_confirmacion else None,
        "detalles_matrimonio": sacramento_data.detalles_matrimonio.model_dump() if sacramento_data.detalles_matrimonio else None
    }
    
    fake_sacramentos_db[sacramento_id_counter] = nuevo_sacramento
    sacramento_id_counter += 1
    
    return SacramentoResponse(**nuevo_sacramento)


@router.get("/", response_model=List[SacramentoResponse])
async def get_sacramentos(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
    tipo_sacramento: Optional[str] = Query(None, description="Filtrar por tipo (bautizo, confirmacion, matrimonio)"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    parroquia: Optional[str] = Query(None, description="Filtrar por parroquia"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de sacramentos.
    """
    # Filtrar sacramentos
    filtered_sacramentos = list(fake_sacramentos_db.values())
    
    if tipo_sacramento:
        filtered_sacramentos = [
            s for s in filtered_sacramentos 
            if s["tipo_sacramento"] == tipo_sacramento
        ]
    
    if fecha_desde:
        filtered_sacramentos = [
            s for s in filtered_sacramentos 
            if s["fecha_sacramento"] >= fecha_desde
        ]
        
    if fecha_hasta:
        filtered_sacramentos = [
            s for s in filtered_sacramentos 
            if s["fecha_sacramento"] <= fecha_hasta
        ]
    
    if parroquia:
        parroquia_lower = parroquia.lower()
        filtered_sacramentos = [
            s for s in filtered_sacramentos 
            if parroquia_lower in s["parroquia"].lower()
        ]
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_sacramentos = filtered_sacramentos[start:end]
    
    return [SacramentoResponse(**sacramento) for sacramento in paginated_sacramentos]


@router.get("/bautizos/buscar", response_model=List[SacramentoResponse])
async def buscar_bautizos(
    busqueda: BautizoBusqueda = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Búsqueda específica para bautizos.
    """
    # Filtrar solo bautizos
    bautizos = [
        s for s in fake_sacramentos_db.values() 
        if s["tipo_sacramento"] == "bautizo"
    ]
    
    # Aplicar filtros específicos de bautizo
    if busqueda.nombre_padrino:
        padrino_lower = busqueda.nombre_padrino.lower()
        bautizos = [
            b for b in bautizos 
            if b.get("detalles_bautizo") and 
            padrino_lower in (b["detalles_bautizo"].get("nombre_padrino") or "").lower()
        ]
    
    if busqueda.nombre_madrina:
        madrina_lower = busqueda.nombre_madrina.lower()
        bautizos = [
            b for b in bautizos 
            if b.get("detalles_bautizo") and 
            madrina_lower in (b["detalles_bautizo"].get("nombre_madrina") or "").lower()
        ]
    
    return [SacramentoResponse(**bautizo) for bautizo in bautizos]


@router.get("/confirmaciones/buscar", response_model=List[SacramentoResponse])
async def buscar_confirmaciones(
    busqueda: ConfirmacionBusqueda = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Búsqueda específica para confirmaciones.
    """
    # Filtrar solo confirmaciones
    confirmaciones = [
        s for s in fake_sacramentos_db.values() 
        if s["tipo_sacramento"] == "confirmacion"
    ]
    
    # Aplicar filtros específicos de confirmación
    if busqueda.nombre_padrino:
        padrino_lower = busqueda.nombre_padrino.lower()
        confirmaciones = [
            c for c in confirmaciones 
            if c.get("detalles_confirmacion") and 
            padrino_lower in (c["detalles_confirmacion"].get("nombre_padrino") or "").lower()
        ]
    
    return [SacramentoResponse(**confirmacion) for confirmacion in confirmaciones]


@router.get("/matrimonios/buscar", response_model=List[SacramentoResponse])
async def buscar_matrimonios(
    busqueda: MatrimonioBusqueda = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Búsqueda específica para matrimonios.
    """
    # Filtrar solo matrimonios
    matrimonios = [
        s for s in fake_sacramentos_db.values() 
        if s["tipo_sacramento"] == "matrimonio"
    ]
    
    # Aplicar filtros específicos de matrimonio
    if busqueda.nombre_testigo1:
        testigo1_lower = busqueda.nombre_testigo1.lower()
        matrimonios = [
            m for m in matrimonios 
            if m.get("detalles_matrimonio") and 
            testigo1_lower in (m["detalles_matrimonio"].get("nombre_testigo1") or "").lower()
        ]
    
    if busqueda.nombre_testigo2:
        testigo2_lower = busqueda.nombre_testigo2.lower()
        matrimonios = [
            m for m in matrimonios 
            if m.get("detalles_matrimonio") and 
            testigo2_lower in (m["detalles_matrimonio"].get("nombre_testigo2") or "").lower()
        ]
    
    return [SacramentoResponse(**matrimonio) for matrimonio in matrimonios]


@router.get("/{sacramento_id}", response_model=SacramentoResponse)
async def get_sacramento_by_id(
    sacramento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un sacramento por su ID.
    """
    sacramento = fake_sacramentos_db.get(sacramento_id)
    if not sacramento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacramento no encontrado"
        )
    
    return SacramentoResponse(**sacramento)


@router.put("/{sacramento_id}", response_model=SacramentoResponse)
async def update_sacramento(
    sacramento_id: int,
    sacramento_update: SacramentoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza la información de un sacramento.
    
    Requiere permisos de sacerdote, secretario o administrador.
    """
    # Verificar permisos
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote", "secretario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar sacramentos"
        )
    
    sacramento = fake_sacramentos_db.get(sacramento_id)
    if not sacramento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacramento no encontrado"
        )
    
    # Obtener datos a actualizar
    update_data = sacramento_update.model_dump(exclude_unset=True)
    
    # Actualizar campos
    for field, value in update_data.items():
        if field in ["detalles_bautizo", "detalles_confirmacion", "detalles_matrimonio"] and value:
            sacramento[field] = value.model_dump() if hasattr(value, 'model_dump') else value
        else:
            sacramento[field] = value
    
    return SacramentoResponse(**sacramento)


@router.delete("/{sacramento_id}", response_model=MessageResponse)
async def delete_sacramento(
    sacramento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un sacramento del sistema.
    
    Solo administradores pueden eliminar sacramentos.
    """
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar sacramentos"
        )
    
    if sacramento_id not in fake_sacramentos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacramento no encontrado"
        )
    
    del fake_sacramentos_db[sacramento_id]
    
    return MessageResponse(
        message="Sacramento eliminado exitosamente",
        success=True
    )


@router.get("/persona/{persona_id}", response_model=List[SacramentoResponse])
async def get_sacramentos_by_persona(
    persona_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todos los sacramentos de una persona específica.
    """
    # Verificar que la persona existe
    if persona_id not in fake_personas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona no encontrada"
        )
    
    # Obtener sacramentos de la persona
    sacramentos_persona = [
        s for s in fake_sacramentos_db.values() 
        if s["id_persona"] == persona_id
    ]
    
    return [SacramentoResponse(**sacramento) for sacramento in sacramentos_persona]