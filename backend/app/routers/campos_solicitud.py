from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.solicitudes import CampoSolicitud

router = APIRouter()


class CampoSolicitudBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    tipo_dato: str = Field(default="texto", max_length=20)  # texto/numero/fecha/booleano/lista
    opciones: Optional[List[str]] = None
    obligatorio: bool = False
    activo: bool = True
    orden: int = 0


class CampoSolicitudCreate(CampoSolicitudBase):
    pass


class CampoSolicitudUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    tipo_dato: Optional[str] = Field(None, max_length=20)
    opciones: Optional[List[str]] = None
    obligatorio: Optional[bool] = None
    activo: Optional[bool] = None
    orden: Optional[int] = None


class CampoSolicitudOut(CampoSolicitudBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


@router.get("/campos-solicitud", response_model=List[CampoSolicitudOut])
def listar_campos(solo_activos: bool = False, db: Session = Depends(get_db)):
    q = db.query(CampoSolicitud)
    if solo_activos:
        q = q.filter(CampoSolicitud.activo.is_(True))
    return q.order_by(CampoSolicitud.orden, CampoSolicitud.id).all()


@router.post(
    "/campos-solicitud",
    response_model=CampoSolicitudOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_campo(obj_in: CampoSolicitudCreate, db: Session = Depends(get_db)):
    campo = CampoSolicitud(**obj_in.model_dump())
    db.add(campo)
    db.commit()
    db.refresh(campo)
    return campo


@router.put("/campos-solicitud/{id}", response_model=CampoSolicitudOut)
def actualizar_campo(id: int, obj_in: CampoSolicitudUpdate, db: Session = Depends(get_db)):
    campo = db.query(CampoSolicitud).filter(CampoSolicitud.id == id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(campo, field, value)
    db.commit()
    db.refresh(campo)
    return campo


@router.delete("/campos-solicitud/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_campo(id: int, db: Session = Depends(get_db)):
    campo = db.query(CampoSolicitud).filter(CampoSolicitud.id == id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    db.delete(campo)
    db.commit()
