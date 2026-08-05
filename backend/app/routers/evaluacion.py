from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.evaluacion import CriterioEvaluacion

router = APIRouter(prefix="/criterios-evaluacion")


class CriterioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    clave: str
    nombre: str
    descripcion: Optional[str] = None
    peso_default: Decimal
    orden: int
    activo: bool


class CriterioUpdate(BaseModel):
    peso_default: Optional[Decimal] = None
    activo: Optional[bool] = None


@router.get("", response_model=List[CriterioOut])
def listar_criterios(db: Session = Depends(get_db)):
    return (
        db.query(CriterioEvaluacion)
        .order_by(CriterioEvaluacion.orden)
        .all()
    )


@router.put("/{clave}", response_model=CriterioOut)
def actualizar_criterio(clave: str, data: CriterioUpdate, db: Session = Depends(get_db)):
    criterio = db.query(CriterioEvaluacion).filter(CriterioEvaluacion.clave == clave).first()
    if not criterio:
        raise HTTPException(status_code=404, detail="Criterio no encontrado.")
    if data.peso_default is not None:
        if data.peso_default < 0 or data.peso_default > 100:
            raise HTTPException(status_code=400, detail="El peso debe estar entre 0 y 100.")
        criterio.peso_default = data.peso_default
    if data.activo is not None:
        criterio.activo = data.activo
    db.commit()
    db.refresh(criterio)
    return criterio


@router.put("", response_model=List[CriterioOut])
def actualizar_pesos_masivo(pesos: dict[str, Decimal], db: Session = Depends(get_db)):
    """Actualiza varios pesos a la vez. Valida que la suma de los activos sea 100."""
    criterios = db.query(CriterioEvaluacion).all()
    mapa = {c.clave: c for c in criterios}
    for clave, peso in pesos.items():
        if clave not in mapa:
            raise HTTPException(status_code=400, detail=f"Criterio desconocido: {clave}")
        if peso < 0 or peso > 100:
            raise HTTPException(status_code=400, detail="Cada peso debe estar entre 0 y 100.")
        mapa[clave].peso_default = peso
    total = sum(c.peso_default for c in criterios if c.activo)
    if round(total) != 100:
        raise HTTPException(status_code=400, detail=f"Los pesos de los criterios activos deben sumar 100 (actual: {total}).")
    db.commit()
    return db.query(CriterioEvaluacion).order_by(CriterioEvaluacion.orden).all()
