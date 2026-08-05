from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.trm import TasaCambio, HistorialTasaCambio

router = APIRouter(prefix="/trm")

MONEDAS_SOPORTADAS = {"USD", "EUR", "GBP"}


class TasaCambioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    moneda: str
    tasa_cop: Decimal
    updated_at: datetime


class HistorialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    moneda: str
    tasa_cop_anterior: Optional[Decimal]
    tasa_cop_nueva: Decimal
    usuario: Optional[str]
    created_at: datetime


class TasaCambioUpdate(BaseModel):
    tasa_cop: Decimal
    usuario: Optional[str] = None


@router.get("", response_model=List[TasaCambioOut])
def listar_tasas(db: Session = Depends(get_db)):
    return db.query(TasaCambio).order_by(TasaCambio.moneda).all()


@router.put("/{moneda}", response_model=TasaCambioOut)
def actualizar_tasa(moneda: str, data: TasaCambioUpdate, db: Session = Depends(get_db)):
    moneda = moneda.upper()
    if moneda not in MONEDAS_SOPORTADAS:
        raise HTTPException(status_code=400, detail=f"Moneda no soportada. Válidas: {', '.join(sorted(MONEDAS_SOPORTADAS))}")
    if data.tasa_cop <= 0:
        raise HTTPException(status_code=400, detail="La tasa debe ser mayor a cero.")

    tasa = db.query(TasaCambio).filter(TasaCambio.moneda == moneda).first()
    tasa_anterior = tasa.tasa_cop if tasa else None

    # Guardar historial antes de actualizar
    historial = HistorialTasaCambio(
        moneda=moneda,
        tasa_cop_anterior=tasa_anterior,
        tasa_cop_nueva=data.tasa_cop,
        usuario=data.usuario,
    )
    db.add(historial)

    if tasa:
        tasa.tasa_cop = data.tasa_cop
        tasa.updated_at = datetime.utcnow()
    else:
        tasa = TasaCambio(moneda=moneda, tasa_cop=data.tasa_cop)
        db.add(tasa)

    db.commit()
    db.refresh(tasa)
    return tasa


@router.get("/{moneda}/historial", response_model=List[HistorialOut])
def historial_tasa(moneda: str, limit: int = 30, db: Session = Depends(get_db)):
    moneda = moneda.upper()
    return (
        db.query(HistorialTasaCambio)
        .filter(HistorialTasaCambio.moneda == moneda)
        .order_by(HistorialTasaCambio.created_at.desc())
        .limit(limit)
        .all()
    )
