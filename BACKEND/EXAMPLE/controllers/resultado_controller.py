from fastapi import APIRouter, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from typing import Annotated

from app.dto.resultado_dto import ResultadoCreateDTO, ResultadoUpdateDTO, ResultadoOutDTO
from app.services.resultado_service import ResultadoService

try:
    from pocketbase.client import ClientResponseError
except Exception:
    from pocketbase.utils import ClientResponseError

router = APIRouter(prefix="/api/resultados", tags=["resultados"])

def _pb_raise(e: ClientResponseError):
    # Manejo correcto de ClientResponseError
    error_message = getattr(e, 'message', None) or str(e)
    error_data = getattr(e, 'data', None)
    status_code = getattr(e, 'status', None) or 400
    
    # Si hay data específica de PocketBase, usarla
    if error_data:
        detail = error_data
    else:
        detail = error_message
    
    raise HTTPException(status_code=status_code, detail=detail)

IdPB = Annotated[str, Path(pattern=r"^[a-z0-9]{15}$", description="ID de PocketBase")]

@router.post("", status_code=status.HTTP_201_CREATED)
def crear(dto: ResultadoCreateDTO = Body(...)):
    try:
        ResultadoService.create(dto)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": "Resultado creado exitosamente"})
    except ClientResponseError as e:
        _pb_raise(e)

@router.get("/{id}", response_model=ResultadoOutDTO)
def obtener(id: IdPB):
    try:
        r = ResultadoService.get(id)
        return ResultadoOutDTO.model_validate(r.__dict__)
    except ClientResponseError as e:
        _pb_raise(e)

@router.get("")
def listar(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    filtro: str | None = Query(default=None, description='Filtro PB, ej: id_test="..."'),
    solo_activos: bool = Query(default=True, description="Si true, lista solo active=true"),
):
    try:
        return ResultadoService.list(page, per_page, filtro, solo_activos)
    except ClientResponseError as e:
        _pb_raise(e)

@router.patch("/{id}", response_model=ResultadoOutDTO)
def actualizar(id: IdPB, dto: ResultadoUpdateDTO = Body(...)):
    try:
        r = ResultadoService.update(id, dto)
        return ResultadoOutDTO.model_validate(r.__dict__)
    except ClientResponseError as e:
        _pb_raise(e)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def desactivar(id: IdPB):
    try:
        ResultadoService.soft_delete(id)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Resultado desactivado correctamente"})
    except ClientResponseError as e:
        _pb_raise(e)
