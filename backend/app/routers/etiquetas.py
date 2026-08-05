from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.etiquetas import crud_dimension, crud_etiqueta
from app.database import get_db
from app.schemas.etiquetas import (
    DimensionCreate, DimensionListOut, DimensionOut, DimensionUpdate,
    EtiquetaCreate, EtiquetaListOut, EtiquetaOut, EtiquetaUpdate,
)

router = APIRouter()


# ─── Categorías ──────────────────────────────────────────────────────────────

@router.get("/dimensiones", response_model=DimensionListOut)
def listar_dimensiones(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    items, total = crud_dimension.get_multi_filtered(db, skip=skip, limit=limit)
    return DimensionListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/dimensiones", response_model=DimensionOut, status_code=status.HTTP_201_CREATED)
def crear_dimension(
    obj_in: DimensionCreate,
    db: Session = Depends(get_db),
):
    return crud_dimension.create(db, obj_in=obj_in)


@router.get("/dimensiones/{id}", response_model=DimensionOut)
def obtener_dimension(id: int, db: Session = Depends(get_db)):
    obj = crud_dimension.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return obj


@router.put("/dimensiones/{id}", response_model=DimensionOut)
def actualizar_dimension(
    id: int,
    obj_in: DimensionUpdate,
    db: Session = Depends(get_db),
):
    obj = crud_dimension.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return crud_dimension.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/dimensiones/{id}", response_model=DimensionOut)
def eliminar_dimension(id: int, db: Session = Depends(get_db)):
    obj = crud_dimension.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return obj


# ─── Etiquetas ────────────────────────────────────────────────────────────────

@router.get("/etiquetas", response_model=EtiquetaListOut)
def listar_etiquetas(
    skip: int = 0,
    limit: int = 20,
    dimension_id: Optional[int] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    items, total = crud_etiqueta.get_multi_filtered(
        db, skip=skip, limit=limit, dimension_id=dimension_id, activo=activo
    )
    return EtiquetaListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/etiquetas", response_model=EtiquetaOut, status_code=status.HTTP_201_CREATED)
def crear_etiqueta(
    obj_in: EtiquetaCreate,
    db: Session = Depends(get_db),
):
    return crud_etiqueta.create(db, obj_in=obj_in)


@router.get("/etiquetas/{id}", response_model=EtiquetaOut)
def obtener_etiqueta(id: int, db: Session = Depends(get_db)):
    obj = crud_etiqueta.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return obj


@router.put("/etiquetas/{id}", response_model=EtiquetaOut)
def actualizar_etiqueta(
    id: int,
    obj_in: EtiquetaUpdate,
    db: Session = Depends(get_db),
):
    obj = crud_etiqueta.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return crud_etiqueta.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/etiquetas/{id}", response_model=EtiquetaOut)
def eliminar_etiqueta(id: int, db: Session = Depends(get_db)):
    obj = crud_etiqueta.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return obj
