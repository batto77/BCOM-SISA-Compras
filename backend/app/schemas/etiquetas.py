from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# --- Dimension ---

class DimensionBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class DimensionCreate(DimensionBase):
    pass


class DimensionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class DimensionOut(DimensionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class DimensionListOut(BaseModel):
    items: List[DimensionOut]
    total: int
    skip: int
    limit: int


# --- Etiqueta ---

class EtiquetaBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    dimension_id: Optional[int] = None
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class EtiquetaCreate(EtiquetaBase):
    pass


class EtiquetaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    dimension_id: Optional[int] = None
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class EtiquetaOut(EtiquetaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    dimension: Optional[DimensionOut] = None


class EtiquetaListOut(BaseModel):
    items: List[EtiquetaOut]
    total: int
    skip: int
    limit: int
